from __future__ import annotations

import json
from dataclasses import dataclass
from msilib.schema import Component
from pathlib import Path

from aenum import Enum, auto

from sym_cps.grammar.tools import get_direction_from_components_and_connections
from sym_cps.shared.library import c_library
from sym_cps.shared.objects import default_parameters, structures
from sym_cps.tools.strings import get_component_type_from_instance_name


class AbstractionFeatures(Enum):
    AVOID_REDUNDANT_CONNECTIONS = auto()
    USE_DEFAULT_PARAMETERS = auto()
    USE_STRUCTURES = auto()


abstraction_levels_features = {
    1: {},
    2: {AbstractionFeatures.USE_DEFAULT_PARAMETERS},
    3: {AbstractionFeatures.USE_DEFAULT_PARAMETERS, AbstractionFeatures.AVOID_REDUNDANT_CONNECTIONS},
    4: {
        AbstractionFeatures.AVOID_REDUNDANT_CONNECTIONS,
        AbstractionFeatures.USE_DEFAULT_PARAMETERS,
        AbstractionFeatures.USE_STRUCTURES,
    },
}


""" TODO: implement condition 'AVOID_REDUNDANT_CONNECTIONS'
A connection is redundant, i.e. Tube - Wing - TOP  == Wing - Tube - Bottom
 Check "connectors_compoennts_mapping.json" and avoid redundancies
"""


""" TODO: implement condition 'USE_STRUCTURES'
 identify and define structure and build another abstraction layer.
A structure is a cluster of nodes, for example a Propeller + Motor + Flange. 
Since they always go together they can be grouped in a strucutre
"""


@dataclass
class AbstractTopology:
    name: str
    description: str
    connections: dict[str, dict[str, str]]
    parameters: dict[str, dict[str, float]]

    @classmethod
    def from_json(cls, topology_json_path: Path) -> AbstractTopology:
        topo = json.load(open(topology_json_path))
        name = topo["NAME"]
        description = topo["DESCRIPTION"]
        abstraction_level = topo["ABSTRACTION_LEVEL"]
        connections: dict[str, dict[str, str]] = {}
        parameters: dict[str, dict[str, str]] = {}

        # unravel structure prior to looping through topology then proceed as normal
        if AbstractionFeatures.USE_STRUCTURES in abstraction_levels_features[abstraction_level]:
            for component_a, categories in topo["TOPOLOGY"].items():
                # ex. component_a == "PROPELLER_STRUCTURE_TOP_instance_1"
                split_str = component_a.split('_')
                struct = split_str[0] + '_' + split_str[1] + '_' + split_str[2]
                if struct in structures.keys():
                    topo_instance = {}
                    instance = '_' + split_str[3] + '_' + split_str[4]
                    component_interface = structures[struct]["InterfaceComponent"]
                    for struct_component in structures[struct]["Components"]:
                        #instantiate set of components and connect to one another
                        # ex. component_a == "PROPELLER_STRUCTURE_TOP_instance_1" and comp_a == "Motor"
                        # component => "Motor_instance_1"
                        for comp_a in struct_component.keys():
                            topo_instance[comp_a + instance] = {
                                "CONNECTIONS": {},
                                "PARAMETERS": {}
                            }
                            # if comp_a == "Flange" then attach tube connections to flange
                            if comp_a == component_interface:
                                topo_instance[comp_a + instance]["CONNECTIONS"] = topo["TOPOLOGY"]["CONNECTIONS"]
                            for struct_category in struct_component[comp_a].key():
                                if struct_category == "CONNECTIONS":
                                    # append instance to each of the connections as well
                                    for comp_b in struct_component[comp_a][struct_category].keys():
                                        topo_instance[comp_a + instance]["CONNECTIONS"][comp_b + instance] = struct_component[comp_a][struct_category][comp_b]
                                else:
                                    topo_instance[struct_component + instance]["PARAMETERS"] = structures[struct][struct_component][struct_category]
                            topo[comp_a + instance] = topo_instance[struct_component + instance]
                            # remove structure key from topo
                        del topo[component_a]
                else:
                    continue


        for component_a, categories in topo["TOPOLOGY"].items():
            for category, infos in categories.items():
                if category == "CONNECTIONS":
                    if component_a not in connections:
                        connections[component_a] = {}

                    for component_b, direction in infos.items():
                        connections[component_a][component_b] = direction

                        if (
                            AbstractionFeatures.AVOID_REDUNDANT_CONNECTIONS
                            in abstraction_levels_features[abstraction_level]
                        ):
                            ctype_a_str = get_component_type_from_instance_name(component_a)
                            ctype_a = c_library.component_types[ctype_a_str]
                            ctype_b_str = get_component_type_from_instance_name(component_b)
                            ctype_b = c_library.component_types[ctype_b_str]
                            connectors = c_library.get_connectors(ctype_a, ctype_b, direction)
                            connector_id_a = connectors[0].id
                            connector_id_b = connectors[1].id

                            if component_b not in connections:
                                connections[component_b] = {}

                            connections[component_b][component_a] = get_direction_from_components_and_connections(
                                ctype_b.id, ctype_a.id, connector_id_b, connector_id_a
                            )
                if category == "PARAMETERS":
                    if component_a not in parameters:
                        parameters[component_a] = {}
                    if AbstractionFeatures.USE_DEFAULT_PARAMETERS in abstraction_levels_features[abstraction_level]:
                        c_type: str = get_component_type_from_instance_name(component_a)
                        for parameter in c_library.component_types[c_type].parameters.values():
                            if parameter.id in default_parameters.keys():
                                parameters[component_a][parameter.id] = float(default_parameters[parameter.id])
                    for param, value in infos.items():
                        parameters[component_a][param] = float(value)
        return cls(name, description, connections, parameters)

    def to_json(self, abstraction_level: int) -> str:
        export: dict = {"NAME": self.name, "DESCRIPTION": "", "ABSTRACTION_LEVEL": abstraction_level, "TOPOLOGY": {}}

        for component_a, connections in self.connections.items():
            export["TOPOLOGY"][component_a] = {"CONNECTIONS": {}, "PARAMETERS": {}}
            """Parameters"""
            if component_a in self.parameters.keys():
                for param, value in self.parameters[component_a].items():
                    if AbstractionFeatures.USE_DEFAULT_PARAMETERS in abstraction_levels_features[abstraction_level]:
                        if param in default_parameters.keys():
                            continue
                    export["TOPOLOGY"][component_a]["PARAMETERS"][param] = value
            """Connections"""
            for component_b, direction in connections.items():
                print(export["TOPOLOGY"][component_a])
                if AbstractionFeatures.AVOID_REDUNDANT_CONNECTIONS in abstraction_levels_features[abstraction_level]:
                    if component_b in list(export["TOPOLOGY"].keys()) and component_a in list(
                        export["TOPOLOGY"][component_b]["CONNECTIONS"].keys()
                    ):
                        continue
                export["TOPOLOGY"][component_a]["CONNECTIONS"][component_b] = direction
        return str(json.dumps(export, indent=4, sort_keys=True))
