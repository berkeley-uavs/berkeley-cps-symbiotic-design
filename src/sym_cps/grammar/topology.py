from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from aenum import Enum, auto

from sym_cps.grammar.abstract_design import AbstractDesign
# from sym_cps.grammar.structures import Structure
from sym_cps.grammar.tools import get_direction_from_components_and_connections, get_opposing_direction_from_components
from sym_cps.shared.library import c_library
from sym_cps.shared.objects import default_parameters, structures
from sym_cps.tools.strings import (
    get_component_and_instance_type_from_instance_name,
    get_component_type_from_instance_name,
    get_instance_name
)

"""TODO REFACTOR"""


class AbstractionFeatures(Enum):
    AVOID_REDUNDANT_CONNECTIONS = auto()
    USE_DEFAULT_PARAMETERS = auto()
    USE_STRUCTURES = auto()
    HIDE_TUBE_CONNECTIONS = auto()


abstraction_levels_features = {
    1: {},
    2: {AbstractionFeatures.USE_DEFAULT_PARAMETERS},
    3: {AbstractionFeatures.USE_DEFAULT_PARAMETERS, AbstractionFeatures.AVOID_REDUNDANT_CONNECTIONS},
    4: {
        AbstractionFeatures.USE_DEFAULT_PARAMETERS,
        AbstractionFeatures.USE_STRUCTURES,
    },
    5: {
        AbstractionFeatures.USE_DEFAULT_PARAMETERS,
        AbstractionFeatures.USE_STRUCTURES,
        AbstractionFeatures.HIDE_TUBE_CONNECTIONS,
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
    abstract_design: AbstractDesign | None = None


    @classmethod
    def from_json(cls, topology_json_path: Path) -> AbstractTopology:
        return AbstractTopology.from_dict(json.load(open(topology_json_path)))

    @classmethod
    def from_dict(cls, topo: dict) -> AbstractTopology:
        name = topo["NAME"]
        description = topo["DESCRIPTION"]
        abstraction_level = topo["ABSTRACTION_LEVEL"]
        connections: dict[str, dict[str, str]] = {}
        parameters: dict[str, dict[str, str]] = {}

        if AbstractionFeatures.USE_STRUCTURES in abstraction_levels_features[abstraction_level]:
            topo = AbstractTopology.unravel_structures(topo=topo)

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

    @classmethod
    def unravel_structures(cls, topo) -> dict:
        # unravel structure prior to looping through topology then proceed as normal
        to_delete = set()
        to_add_topo = {"TOPOLOGY": {}}
        edit_connections = {}
        prop = -1
        for component_a, categories in topo["TOPOLOGY"].items():
            # ex. component_a == "PROPELLER_STRUCTURE_TOP_instance_1"
            if "Orient" in component_a:
                component_a = "Orient"
            struct, instance_n = get_component_and_instance_type_from_instance_name(component_a)
            if struct in structures.keys():
                paramters = [
                    param.split("__")[0] for param in list(topo["TOPOLOGY"][component_a]["PARAMETERS"].keys())
                ]
                instance_n = int(instance_n[0])
                topo_instance = {}
                component_interface = structures[struct]["InterfaceComponent"]
                for struct_component in structures[struct]["Components"]:
                    # instantiate set of components and connect to one another
                    # ex. component_a == "PROPELLER_STRUCTURE_TOP_instance_1" and comp_a == "Motor"
                    # component => "Motor_instance_1"
                    for comp_a in struct_component.keys():
                        if comp_a == "Battery":
                            first_instance = 2 * int(instance_n) - 1
                            second_instance = 2 * int(instance_n)
                            topo_instance[get_instance_name(comp_a, first_instance)] = {
                                "CONNECTIONS": {},
                                "PARAMETERS": {},
                            }
                            topo_instance[get_instance_name(comp_a, second_instance)] = {
                                "CONNECTIONS": {},
                                "PARAMETERS": {},
                            }
                        else:
                            """TODO REFACTOR"""
                            topo_instance[get_instance_name(comp_a, instance_n)] = {
                                "CONNECTIONS": {},
                                "PARAMETERS": {},
                            }

                        # if comp_a == "Flange" then attach tube connections to flange
                        # if comp_a == component_interface:
                        #     topo_instance[comp_a + "_instance_" + str(instance_n)]["CONNECTIONS"] = \
                        #         topo["TOPOLOGY"][component_a]["CONNECTIONS"]
                        for struct_category in struct_component[comp_a].keys():
                            if struct_category == "CONNECTIONS":
                                # append instance to each of the connections as well
                                for comp_b in struct_component[comp_a][struct_category].keys():
                                    if comp_b in c_library.component_types[comp_a].compatible_with.keys():
                                        key_a = get_instance_name(comp_a, instance_n)
                                        key_b = get_instance_name(comp_b, instance_n)
                                        if comp_b == "BatteryController":
                                            topo_instance[key_a]["CONNECTIONS"][
                                                comp_b + "_instance_1"
                                            ] = struct_component[comp_a][struct_category][comp_b]
                                        elif comp_a == "Battery":
                                            topo_instance[get_instance_name(comp_a, first_instance)][
                                                "CONNECTIONS"
                                            ][key_b] = "BOTTOM-2"
                                            topo_instance[get_instance_name(comp_a, second_instance)][
                                                "CONNECTIONS"
                                            ][key_b] = "BOTTOM-1"
                                        elif comp_b == "Battery":
                                            topo_instance[key_a]["CONNECTIONS"][
                                                get_instance_name(comp_b, first_instance)
                                            ] = "INSIDE-2"
                                            topo_instance[key_a]["CONNECTIONS"][
                                                get_instance_name(comp_b, second_instance)
                                            ] = "INSIDE-1"
                                        else:
                                            if "Orient" in comp_a:
                                                key_a = "Orient"
                                            if "Orient" in comp_b:
                                                key_b = "Orient"
                                            topo_instance[key_a]["CONNECTIONS"][
                                                key_b
                                            ] = struct_component[comp_a][struct_category][comp_b]
                            elif struct_category == "PARAMETERS":
                                # if paramter in specified at the structural level, then include that value in
                                # their respective component
                                if comp_a in paramters:
                                    key_a = get_instance_name(comp_a, instance_n)
                                    for i in range(len(paramters)):
                                        if comp_a == paramters[i]:
                                            param_name = list(topo["TOPOLOGY"][component_a]["PARAMETERS"].keys())[i]
                                            value = topo["TOPOLOGY"][component_a]["PARAMETERS"][param_name]
                                            topo_instance[key_a]["PARAMETERS"][
                                                param_name
                                            ] = value
                                elif comp_a == "Motor":
                                    topo_instance[key_a]["PARAMETERS"][
                                        "Motor__CONTROL_CHANNEL"
                                    ] = float(instance_n)
                                elif comp_a == "Propeller":
                                    topo_instance[key_a]["PARAMETERS"][
                                        "Propeller__Direction"
                                    ] = float(prop)
                                    topo_instance[key_a]["PARAMETERS"][
                                        "Propeller__Prop_type"
                                    ] = float(prop)
                                    prop = prop * -1
                                else:
                                    params = struct_component[comp_a][struct_category]
                                    if comp_a == "Battery":
                                        topo_instance[get_instance_name(comp_a, first_instance)][
                                            "PARAMETERS"
                                        ] = params
                                        topo_instance[get_instance_name(comp_a, second_instance)][
                                            "PARAMETERS"
                                        ] = params
                                    else:
                                        key = get_instance_name(comp_a, instance_n)
                                        if "Orient" in comp_a:
                                            key = "Orient"
                                        topo_instance[key][
                                            "PARAMETERS"
                                        ] = params

                            else:
                                raise Exception("Unknown category")
                        if comp_a == "Battery":
                            to_add_topo["TOPOLOGY"][get_instance_name(comp_a, first_instance)] = topo_instance[
                                get_instance_name(comp_a, first_instance)
                            ]
                            to_add_topo["TOPOLOGY"][get_instance_name(comp_a, second_instance)] = topo_instance[
                                get_instance_name(comp_a, second_instance)
                            ]
                        else:
                            key = get_instance_name(comp_a, instance_n)
                            if "Orient" in comp_a:
                                key = "Orient"
                            to_add_topo["TOPOLOGY"][key] = topo_instance[
                                key
                            ]
                to_delete.add(component_a)
            else:
                # if "Propeller_str_top" is in connections, we'll want to change the connection name to Flange
                for connected in topo["TOPOLOGY"][component_a]["CONNECTIONS"].keys():
                    # ex.connected == "Propeller_str_top_instance_1"
                    struct, instance_n = get_component_and_instance_type_from_instance_name(connected)
                    if struct in structures.keys():
                        instance_n = instance_n[0]
                        if not component_a in edit_connections.keys():
                            edit_connections[component_a] = []
                        comp_a_type = get_component_type_from_instance_name(component_a)
                        to_delete.add(connected)
                        for comps in structures[struct]["Components"]:
                            curr = list(comps.keys())[0]
                            if comp_a_type in c_library.component_types[curr].compatible_with.keys():
                                if curr == "Battery":
                                    first_instance = 2 * int(instance_n) - 1
                                    second_instance = 2 * int(instance_n)
                                    edit_connections[component_a].append(
                                        {
                                            get_instance_name(curr, first_instance):
                                                topo["TOPOLOGY"][component_a]["CONNECTIONS"][
                                                connected
                                            ]
                                        }
                                    )
                                    edit_connections[component_a].append(
                                        {
                                            get_instance_name(curr, second_instance):
                                                topo["TOPOLOGY"][component_a]["CONNECTIONS"][
                                                connected
                                            ]
                                        }
                                    )
                                else:
                                    edit_connections[component_a].append(
                                        {
                                            get_instance_name(curr, int(instance_n)):
                                                topo["TOPOLOGY"][component_a]["CONNECTIONS"][
                                                connected
                                            ]
                                        }
                                    )

        for elem in to_delete:
            if elem in topo["TOPOLOGY"].keys():
                del topo["TOPOLOGY"][elem]

        for key, elem in to_add_topo["TOPOLOGY"].items():
            topo["TOPOLOGY"][key] = elem

        for key in edit_connections.keys():
            elem_lst = edit_connections[key]  # lst of dictionaries w/ connections that need to be edited
            for comp in elem_lst:
                for instance, direction in comp.items():
                    topo["TOPOLOGY"][key]["CONNECTIONS"][instance] = direction
                    comp_a_type = get_component_type_from_instance_name(instance)
                    comp_b_type = get_component_type_from_instance_name(key)
                    topo["TOPOLOGY"][instance]["CONNECTIONS"][key] = get_opposing_direction_from_components(
                        comp_a_type, comp_b_type, direction, c_library
                    )
            for connection in to_delete:
                if connection in topo["TOPOLOGY"][key]["CONNECTIONS"].keys():
                    del topo["TOPOLOGY"][key]["CONNECTIONS"][connection]

        return topo

    def to_json(self, abstraction_level: int) -> str:
        export_dict = self.to_dict(abstraction_level)
        return str(json.dumps(export_dict, indent=4))

    def to_dict(self, abstraction_level: int) -> dict:
        export: dict = {"NAME": self.name, "DESCRIPTION": "", "ABSTRACTION_LEVEL": abstraction_level, "TOPOLOGY": {}}
        # if level 4 abstraction, we should group the structures during the looping process and remove extraneous
        # components at the end
        if AbstractionFeatures.USE_STRUCTURES in abstraction_levels_features[abstraction_level]:
            to_delete = set()
            structure_components = {}
            for struct in structures.keys():
                structure_components[structures[struct]["CenterComponent"]] = {
                    struct: [list(comps.keys())[0] for comps in structures[struct]["Components"]]
                }

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
                # print(export["TOPOLOGY"][component_a])
                if AbstractionFeatures.AVOID_REDUNDANT_CONNECTIONS in abstraction_levels_features[abstraction_level]:
                    if component_b in list(export["TOPOLOGY"].keys()) and component_a in list(
                        export["TOPOLOGY"][component_b]["CONNECTIONS"].keys()
                    ):
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
                    structure_name, instance_n = get_component_and_instance_type_from_instance_name(item)
                    c_type_a = get_component_type_from_instance_name(key)
                    group = [list(comps.keys())[0] for comps in structures[structure_name]["Components"]]
                    for component_b, direction in self.connections[key].items():
                        c_type_b = get_component_type_from_instance_name(component_b)
                        if c_type_b == "Hub3" and structure_name == "Fuselage_str":
                            c_type_b = "Hub4"
                            # component_b = "Hub4" + "_instance_" + instance_n
                        if c_type_b in group and not component_b in copy.keys():
                            tracker[component_b] = item
                        if key in export["TOPOLOGY"][component_b]["CONNECTIONS"].keys():
                            direction = export["TOPOLOGY"][component_b]["CONNECTIONS"][key]
                            export["TOPOLOGY"][component_b]["CONNECTIONS"][item + "__" + c_type_a] = direction
                            if not c_type_b in group:
                                export["TOPOLOGY"][item]["CONNECTIONS"][
                                    component_b
                                ] = get_opposing_direction_from_components(
                                    c_type_a, c_type_b, direction, c_library
                                )
                            del export["TOPOLOGY"][component_b]["CONNECTIONS"][key]
                    to_delete.add(key)

            for key in to_delete:
                if key in export["TOPOLOGY"].keys():
                    del export["TOPOLOGY"][key]
        return export
