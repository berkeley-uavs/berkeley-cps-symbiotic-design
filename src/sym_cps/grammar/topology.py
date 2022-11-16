from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from aenum import Enum, auto

from sym_cps.grammar.tools import get_direction_from_components_and_connections
from sym_cps.shared.library import c_library
from sym_cps.shared.objects import default_parameters, structures
from sym_cps.tools.strings import get_component_type_from_instance_name, \
    get_component_and_instance_type_from_instance_name


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
        to_delete = set()
        to_add_topo = {"TOPOLOGY": {}}
        edit_connections = {}
        if AbstractionFeatures.USE_STRUCTURES in abstraction_levels_features[abstraction_level]:
            prop = -1
            for component_a, categories in topo["TOPOLOGY"].items():
                # ex. component_a == "PROPELLER_STRUCTURE_TOP_instance_1"
                struct, instance_n = get_component_and_instance_type_from_instance_name(component_a)
                if struct in structures.keys():
                    topo_instance = {}
                    component_interface = structures[struct]["InterfaceComponent"]
                    for struct_component in structures[struct]["Components"]:
                        # instantiate set of components and connect to one another
                        # ex. component_a == "PROPELLER_STRUCTURE_TOP_instance_1" and comp_a == "Motor"
                        # component => "Motor_instance_1"
                        for comp_a in struct_component.keys():
                            topo_instance[comp_a + "_instance_" + str(instance_n)] = {
                                "CONNECTIONS": {},
                                "PARAMETERS": {}
                            }
                            # if comp_a == "Flange" then attach tube connections to flange
                            if comp_a == component_interface:
                                topo_instance[comp_a + "_instance_" + str(instance_n)]["CONNECTIONS"] = \
                                    topo["TOPOLOGY"][component_a]["CONNECTIONS"]
                            for struct_category in struct_component[comp_a].keys():
                                if struct_category == "CONNECTIONS":
                                    # append instance to each of the connections as well
                                    for comp_b in struct_component[comp_a][struct_category].keys():
                                        if comp_b in c_library.component_types[comp_a].compatible_with.keys():
                                            if comp_b == "BatteryController":
                                                continue
                                                # topo_instance[comp_a + "_instance_" + str(instance_n)]["CONNECTIONS"][comp_b + "_instance_1"] = struct_component[comp_a][struct_category][comp_b]
                                            else:
                                                topo_instance[comp_a + "_instance_" + str(instance_n)]["CONNECTIONS"][
                                                    comp_b + "_instance_" + str(instance_n)] = struct_component[comp_a][struct_category][comp_b]
                                elif struct_category == "PARAMETERS":
                                    if comp_a == "Motor":
                                        topo_instance[comp_a + "_instance_" + str(instance_n)]["PARAMETERS"]["Motor__CONTROL_CHANNEL"] = \
                                            float(instance_n)
                                    elif comp_a == "Propeller":
                                        topo_instance[comp_a + "_instance_" + str(instance_n)]["PARAMETERS"]["Propeller__Direction"] = float(prop)
                                        topo_instance[comp_a + "_instance_" + str(instance_n)]["PARAMETERS"]["Propeller__Prop_type"] = float(prop)
                                        prop = prop * -1
                                    else:
                                        topo_instance[comp_a + "_instance_" + str(instance_n)]["PARAMETERS"] = \
                                            struct_component[comp_a][struct_category]

                                else:
                                    raise Exception("Unknown category")
                            to_add_topo["TOPOLOGY"][comp_a + "_instance_" + str(instance_n)] = topo_instance[
                                comp_a + "_instance_" + str(instance_n)]
                            # remove structure key from topo
                    to_delete.add(component_a)
                else:
                    # if "Propeller_str_top" is in connections, we'll want to change the connection name to Flange
                    for connected in topo["TOPOLOGY"][component_a]["CONNECTIONS"].keys():
                        # ex.connected == "Propeller_str_top_instance_1"
                        struct, instance_n = get_component_and_instance_type_from_instance_name(connected)
                        if struct in structures.keys():
                            if not component_a in edit_connections.keys():
                                edit_connections[component_a] = []
                            comp_a_type = get_component_type_from_instance_name(component_a)
                            for comps in structures[struct]["Components"]:
                                curr = list(comps.keys())[0]
                                if comp_a_type in c_library.component_types[curr].compatible_with.keys():
                                    edit_connections[component_a].append({curr + '_instance_' + str(instance_n): topo["TOPOLOGY"][component_a]["CONNECTIONS"][connected]})

            for elem in to_delete:
                del topo["TOPOLOGY"][elem]

            for key, elem in to_add_topo["TOPOLOGY"].items():
                topo["TOPOLOGY"][key] = elem

            for key in edit_connections.keys():
                elem_lst = edit_connections[key] # lst of dictionaries w/ connections that need to be edited
                for comp in elem_lst:
                    for instance, direction in comp.items():
                        topo["TOPOLOGY"][key]["CONNECTIONS"][instance] = direction
                for connection in to_delete:
                    if connection in topo["TOPOLOGY"][key]["CONNECTIONS"].keys():
                        del topo["TOPOLOGY"][key]["CONNECTIONS"][connection]

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
        # if level 4 abstraction, we should group the structures during the looping process and remove extraneous
        # components at the end
        if AbstractionFeatures.USE_STRUCTURES in abstraction_levels_features[abstraction_level]:
            to_delete = set()
            structure_components = {}
            for struct in structures.keys():
                structure_components[structures[struct]["CenterComponent"]] = {struct: [list(comps.keys())[0] for comps in structures[struct]["Components"]]}

            # use this to keep track of which structure a component belongs to
        tracker = {}
        for component_a, connections in self.connections.items():
            if AbstractionFeatures.USE_STRUCTURES in abstraction_levels_features[abstraction_level]:
                c_type_a, instance = get_component_and_instance_type_from_instance_name(component_a)
                for key, items in structure_components.items():
                    if c_type_a == key:
                        structure_instance = list(items.keys())[0] + "_instance_" + str(instance)
                        export["TOPOLOGY"][structure_instance] = {"CONNECTIONS": {}, "PARAMETERS": {}}
                        tracker[component_a] = structure_instance
                        for component_b, direction in connections.items():
                            if component_b in structure_components[c_type_a].values():
                                tracker[component_b] = structure_instance


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
                            export["TOPOLOGY"][component_b]["CONNECTIONS"].keys()):
                        continue
                if AbstractionFeatures.USE_STRUCTURES in abstraction_levels_features[abstraction_level]:
                    if component_b in tracker.keys():
                        export["TOPOLOGY"][component_a]["CONNECTIONS"][tracker[component_b]] = direction
                export["TOPOLOGY"][component_a]["CONNECTIONS"][component_b] = direction

        # if to_delete is not updated that's when we know we've visited every component in our structures
        if AbstractionFeatures.USE_STRUCTURES in abstraction_levels_features[abstraction_level]:
            prev = -1
            while prev < len(to_delete):
                prev = len(to_delete)
                copy = tracker.copy()
                for key, item in copy.items():
                    structure_name = get_component_type_from_instance_name(item)
                    group = [list(comps.keys())[0] for comps in structures[structure_name]["Components"]]
                    for component_b, direction in self.connections[key].items():
                        c_type_b = get_component_type_from_instance_name(component_b)
                        if c_type_b in group and not component_b in copy.keys():
                            tracker[component_b] = item
                        if key in export["TOPOLOGY"][component_b]["CONNECTIONS"].keys():
                            direction = export["TOPOLOGY"][component_b]["CONNECTIONS"][key]
                            export["TOPOLOGY"][component_b]["CONNECTIONS"][item] = direction
                            del export["TOPOLOGY"][component_b]["CONNECTIONS"][key]
                    to_delete.add(key)

            for key in to_delete:
                if key in export["TOPOLOGY"].keys():
                    for comp, direction in export["TOPOLOGY"][key]["CONNECTIONS"].items():
                        if comp != tracker[key]:
                            ctype_a_str = get_component_type_from_instance_name(key)
                            ctype_a = c_library.component_types[ctype_a_str]
                            ctype_b_str = get_component_type_from_instance_name(comp)
                            ctype_b = c_library.component_types[ctype_b_str]
                            connectors = c_library.get_connectors(ctype_a, ctype_b, direction)
                            connector_id_a = connectors[0].id
                            connector_id_b = connectors[1].id

                            export["TOPOLOGY"][comp]['CONNECTIONS'][tracker[key]] = get_direction_from_components_and_connections(
                                ctype_b.id, ctype_a.id, connector_id_b, connector_id_a
                            )
                    del export["TOPOLOGY"][key]

        return str(json.dumps(export))