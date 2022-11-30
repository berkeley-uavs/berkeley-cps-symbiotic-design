from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from aenum import Enum, auto

from sym_cps.grammar.tools import get_direction_from_components_and_connections
from sym_cps.representation.design.abstract import AbstractDesign
from sym_cps.representation.design.concrete import Component, Connection, DConcrete
from sym_cps.shared.library import c_library
from sym_cps.shared.paths import manual_default_parameters_path, structures_path
from sym_cps.tools.strings import (
    get_component_and_instance_type_from_instance_name,
    get_component_type_from_instance_name,
    get_instance_name,
)

"""TODO REFACTOR"""


class HumanFeatures(Enum):
    AVOID_REDUNDANT_CONNECTIONS = auto()
    USE_DEFAULT_PARAMETERS = auto()
    USE_STRUCTURES = auto()
    HIDE_TUBE_CONNECTIONS = auto()


abstraction_levels_features = {
    1: {},
    2: {HumanFeatures.USE_DEFAULT_PARAMETERS},
    3: {HumanFeatures.USE_DEFAULT_PARAMETERS, HumanFeatures.AVOID_REDUNDANT_CONNECTIONS},
    4: {
        HumanFeatures.USE_DEFAULT_PARAMETERS,
        HumanFeatures.USE_STRUCTURES,
    },
    5: {
        HumanFeatures.USE_DEFAULT_PARAMETERS,
        HumanFeatures.USE_STRUCTURES,
        HumanFeatures.HIDE_TUBE_CONNECTIONS,
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
class HumanDesign:
    name: str
    description: str
    connections: dict[str, dict[str, str]]
    parameters: dict[str, dict[str, float]]
    abstract_design: AbstractDesign | None = None

    @classmethod
    def from_concrete(cls, d_concrete: DConcrete) -> HumanDesign:
        name = d_concrete.name
        description = d_concrete.description
        connections: dict[str, dict[str, str]] = {}
        parameters: dict[str, dict[str, float]] = {}

        """Connections"""
        for edge in d_concrete.edges:
            node_id_s = d_concrete.graph.vs[edge.source]["instance"]
            node_id_t = d_concrete.graph.vs[edge.target]["instance"]
            direction = edge["connection"].direction_b_respect_to_a
            if node_id_s not in connections:
                connections[node_id_s] = {}
            connections[node_id_s][node_id_t] = direction

        """Parameters"""
        for node in d_concrete.nodes:
            node_id = node["instance"]
            if node_id not in connections.keys():
                """Adding nodes with no connections"""
                connections[node_id] = {}
            if node_id not in parameters.keys():
                """Adding nodes with no connections"""
                parameters[node_id] = {}
            for parameter_id, parameter in node["component"].parameters.items():
                # print(node["component"])
                parameters[node_id][parameter_id] = float(parameter.value)

        return cls(name, description, connections, parameters)

    def to_concrete(self) -> DConcrete:
        d_concrete = DConcrete(name=self.name)
        for component_id_a, connections in self.connections.items():
            vertex_a = d_concrete.get_node_by_instance(component_id_a)
            if vertex_a is None:
                component_type_id = get_component_type_from_instance_name(component_id_a)
                vertex_a = d_concrete.add_node(
                    Component(c_type=c_library.component_types[component_type_id], id=component_id_a)
                )
            """Parameters"""
            if component_id_a in self.parameters.keys():
                vertex_a["component"].update_parameters(self.parameters[component_id_a])
            """Connections"""
            for component_id_b, direction in connections.items():
                vertex_b = d_concrete.get_node_by_instance(component_id_b)
                if vertex_b is None:
                    component_type_id = get_component_type_from_instance_name(component_id_b)
                    vertex_b = d_concrete.add_node(
                        Component(c_type=c_library.component_types[component_type_id], id=component_id_b)
                    )
                connection = Connection.from_direction(
                    component_a=vertex_a["component"],
                    component_b=vertex_b["component"],
                    direction=direction,
                )
                d_concrete.add_edge(vertex_a, vertex_b, connection)

        return d_concrete

    #
    # @classmethod
    # def from_abstract_design(cls, abstract_design: AbstractDesign) -> HumanDesign:
    #
    #     # goal_example = topo_example.to_dict(4)
    #
    #     export: dict = {"NAME": abstract_design.name, "DESCRIPTION": "", "ABSTRACTION_LEVEL": 4, "TOPOLOGY": {}}
    #
    #     export["TOPOLOGY"] = {}
    #
    #     hubs = abstract_design.instantiate_hubs()
    #     for hub in hubs:
    #         key = list(hub.keys())[0]
    #         value = hub[key]
    #         export["TOPOLOGY"][key] = value
    #
    #     # instantiate BatteryController
    #     export["TOPOLOGY"]["BatteryController_instance_1"] = {"CONNECTIONS": {}, "PARAMETERS": {}}
    #
    #     for position, abstract_component in abstract_design.grid.items():
    #         if abstract_component.base_name == "Connector":
    #             continue
    #         else:
    #             export["TOPOLOGY"][abstract_component.id] = {}
    #             export["TOPOLOGY"][abstract_component.id]["CONNECTIONS"] = {}
    #             export["TOPOLOGY"][abstract_component.id]["PARAMETERS"] = {}
    #             if abstract_component.base_name == "Propeller_str_top":
    #                 export["TOPOLOGY"]["BatteryController_instance_1"]["CONNECTIONS"][
    #                     abstract_component.id + "__Motor"
    #                     ] = "ANY"
    #             if abstract_component.base_name == "Fuselage_str":
    #                 export["TOPOLOGY"]["BatteryController_instance_1"]["CONNECTIONS"][
    #                     abstract_component.id + "__Battery"
    #                     ] = "ANY"
    #
    #     tubes = abstract_design.instantiate_tubes(len(hubs))
    #     for tube in tubes:
    #         key = list(tube.keys())[0]
    #         value = tube[key]
    #         export["TOPOLOGY"][key] = value
    #         for component_b, connection in value["CONNECTIONS"].items():
    #             if get_component_type_from_instance_name(component_b) == "Hub6":
    #                 a, b = connection.split("-")
    #                 export["TOPOLOGY"][component_b]["CONNECTIONS"][key] = b + "-" + a
    #
    #     # if we don't need a batterController just delete it
    #     if len(export["TOPOLOGY"]["BatteryController_instance_1"]["CONNECTIONS"].values()) == 0:
    #         del export["TOPOLOGY"]["BatteryController_instance_1"]
    #
    #     abTop = HumanDesign.from_dict(export)
    #     return abTop

    @classmethod
    def from_json(cls, topology_json_path: Path) -> HumanDesign:
        return HumanDesign.from_dict(json.load(open(topology_json_path)))

    @classmethod
    def from_dict(cls, topo: dict) -> HumanDesign:
        name = topo["NAME"]
        description = topo["DESCRIPTION"]
        abstraction_level = topo["ABSTRACTION_LEVEL"]
        connections: dict[str, dict[str, str]] = {}
        parameters: dict[str, dict[str, str]] = {}

        default_parameters: dict = json.load(open(manual_default_parameters_path))
        structures: dict = json.load(open(structures_path))
        # unravel structure prior to looping through topology then proceed as normal
        to_delete = set()
        to_add_topo = {"TOPOLOGY": {}}
        edit_connections = {}
        if HumanFeatures.USE_STRUCTURES in abstraction_levels_features[abstraction_level]:
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
                    instance_n = instance_n[0]
                    topo_instance = {}
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
                                        temp = c_library.component_types[comp_a].compatible_with.keys()
                                        if comp_b in c_library.component_types[comp_a].compatible_with.keys():
                                            if comp_b == "BatteryController":
                                                topo_instance[comp_a + "_instance_" + str(instance_n)]["CONNECTIONS"][
                                                    comp_b + "_instance_1"
                                                ] = struct_component[comp_a][struct_category][comp_b]
                                            elif comp_a == "Battery":
                                                topo_instance[comp_a + "_instance_" + str(first_instance)][
                                                    "CONNECTIONS"
                                                ][comp_b + "_instance_" + str(instance_n)] = "BOTTOM-2"
                                                topo_instance[comp_a + "_instance_" + str(second_instance)][
                                                    "CONNECTIONS"
                                                ][comp_b + "_instance_" + str(instance_n)] = "BOTTOM-1"
                                            elif comp_b == "Battery":
                                                topo_instance[comp_a + "_instance_" + str(instance_n)]["CONNECTIONS"][
                                                    comp_b + "_instance_" + str(first_instance)
                                                ] = "INSIDE-2"
                                                topo_instance[comp_a + "_instance_" + str(instance_n)]["CONNECTIONS"][
                                                    comp_b + "_instance_" + str(second_instance)
                                                ] = "INSIDE-1"
                                            else:
                                                key_a = comp_a + "_instance_" + str(instance_n)
                                                key_b = comp_b + "_instance_" + str(instance_n)
                                                if "Orient" in comp_a:
                                                    key_a = "Orient"
                                                if "Orient" in comp_b:
                                                    key_b = "Orient"
                                                topo_instance[key_a]["CONNECTIONS"][key_b] = struct_component[comp_a][
                                                    struct_category
                                                ][comp_b]
                                elif struct_category == "PARAMETERS":
                                    # if paramter in specified at the structural level, then include that value in
                                    # their respective component
                                    if comp_a in parameters:
                                        for i in range(len(paramters)):
                                            if comp_a == paramters[i]:
                                                param_name = list(topo["TOPOLOGY"][component_a]["PARAMETERS"].keys())[i]
                                                value = topo["TOPOLOGY"][component_a]["PARAMETERS"][param_name]
                                                topo_instance[comp_a + "_instance_" + str(instance_n)]["PARAMETERS"][
                                                    param_name
                                                ] = value
                                    elif comp_a == "Motor":
                                        topo_instance[comp_a + "_instance_" + str(instance_n)]["PARAMETERS"][
                                            "Motor__CONTROL_CHANNEL"
                                        ] = float(instance_n)
                                    elif comp_a == "Propeller":
                                        topo_instance[comp_a + "_instance_" + str(instance_n)]["PARAMETERS"][
                                            "Propeller__Direction"
                                        ] = float(prop)
                                        topo_instance[comp_a + "_instance_" + str(instance_n)]["PARAMETERS"][
                                            "Propeller__Prop_type"
                                        ] = float(prop)
                                        prop = prop * -1
                                    else:
                                        if comp_a == "Battery":
                                            topo_instance[comp_a + "_instance_" + str(first_instance)][
                                                "PARAMETERS"
                                            ] = struct_component[comp_a][struct_category]
                                            topo_instance[comp_a + "_instance_" + str(second_instance)][
                                                "PARAMETERS"
                                            ] = struct_component[comp_a][struct_category]
                                        else:
                                            """TODO REFACTOR"""

                                            key = comp_a + "_instance_" + str(instance_n)
                                            if "Orient" in comp_a:
                                                key = "Orient"
                                            topo_instance[key]["PARAMETERS"] = struct_component[comp_a][struct_category]

                                else:
                                    raise Exception("Unknown category")
                            if comp_a == "Battery":
                                to_add_topo["TOPOLOGY"][comp_a + "_instance_" + str(first_instance)] = topo_instance[
                                    comp_a + "_instance_" + str(first_instance)
                                ]
                                to_add_topo["TOPOLOGY"][comp_a + "_instance_" + str(second_instance)] = topo_instance[
                                    comp_a + "_instance_" + str(second_instance)
                                ]
                            else:
                                """TODO REFACTOR"""
                                key = comp_a + "_instance_" + str(instance_n)
                                if "Orient" in comp_a:
                                    key = "Orient"
                                to_add_topo["TOPOLOGY"][key] = topo_instance[key]
                            # remove structure key from topo
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
                                                curr
                                                + "_instance_"
                                                + str(first_instance): topo["TOPOLOGY"][component_a]["CONNECTIONS"][
                                                    connected
                                                ]
                                            }
                                        )
                                        edit_connections[component_a].append(
                                            {
                                                curr
                                                + "_instance_"
                                                + str(second_instance): topo["TOPOLOGY"][component_a]["CONNECTIONS"][
                                                    connected
                                                ]
                                            }
                                        )
                                    else:
                                        edit_connections[component_a].append(
                                            {
                                                curr
                                                + "_instance_"
                                                + str(instance_n): topo["TOPOLOGY"][component_a]["CONNECTIONS"][
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
                        ctype_a = c_library.component_types[comp_a_type]
                        ctype_b = c_library.component_types[comp_b_type]
                        connectors = c_library.get_connectors(ctype_b, ctype_a, direction)
                        connector_id_a = connectors[0].id
                        connector_id_b = connectors[1].id
                        topo["TOPOLOGY"][instance]["CONNECTIONS"][key] = get_direction_from_components_and_connections(
                            ctype_a.id, ctype_b.id, connector_id_b, connector_id_a
                        )

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

                        if HumanFeatures.AVOID_REDUNDANT_CONNECTIONS in abstraction_levels_features[abstraction_level]:
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
                    if HumanFeatures.USE_DEFAULT_PARAMETERS in abstraction_levels_features[abstraction_level]:
                        c_type: str = get_component_type_from_instance_name(component_a)
                        for parameter in c_library.component_types[c_type].parameters.values():
                            if parameter.id in default_parameters.keys():
                                parameters[component_a][parameter.id] = float(default_parameters[parameter.id])
                    for param, value in infos.items():
                        parameters[component_a][param] = float(value)

        return cls(name, description, connections, parameters)

    def to_json(self, abstraction_level: int) -> str:
        export_dict = self.to_dict(abstraction_level)
        return str(json.dumps(export_dict, indent=4))

    def to_dict(self, abstraction_level: int) -> dict:
        export: dict = {"NAME": self.name, "DESCRIPTION": "", "ABSTRACTION_LEVEL": abstraction_level, "TOPOLOGY": {}}
        # if level 4 abstraction, we should group the structures during the looping process and remove extraneous
        # components at the end
        default_parameters = json.load(open(manual_default_parameters_path))
        structures: dict = json.load(open(structures_path))
        if HumanFeatures.USE_STRUCTURES in abstraction_levels_features[abstraction_level]:
            to_delete = set()
            structure_components = {}
            for struct in structures.keys():
                structure_components[structures[struct]["CenterComponent"]] = {
                    struct: [list(comps.keys())[0] for comps in structures[struct]["Components"]]
                }

            # use this to keep track of which structure a component belongs to
        tracker = {}
        for component_a, connections in self.connections.items():
            if HumanFeatures.USE_STRUCTURES in abstraction_levels_features[abstraction_level]:
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
                    if HumanFeatures.USE_DEFAULT_PARAMETERS in abstraction_levels_features[abstraction_level]:
                        if param in default_parameters.keys():
                            continue
                    export["TOPOLOGY"][component_a]["PARAMETERS"][param] = value
            """Connections"""
            for component_b, direction in connections.items():
                # print(export["TOPOLOGY"][component_a])
                if HumanFeatures.AVOID_REDUNDANT_CONNECTIONS in abstraction_levels_features[abstraction_level]:
                    if component_b in list(export["TOPOLOGY"].keys()) and component_a in list(
                        export["TOPOLOGY"][component_b]["CONNECTIONS"].keys()
                    ):
                        continue
                if HumanFeatures.USE_STRUCTURES in abstraction_levels_features[abstraction_level]:
                    if component_b in tracker.keys():
                        export["TOPOLOGY"][component_a]["CONNECTIONS"][tracker[component_b]] = direction
                export["TOPOLOGY"][component_a]["CONNECTIONS"][component_b] = direction

        # if to_delete is not updated that's when we know we've visited every component in our structures
        if HumanFeatures.USE_STRUCTURES in abstraction_levels_features[abstraction_level]:
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
                                comp_type_a = c_library.component_types[c_type_a]
                                comp_type_b = c_library.component_types[c_type_b]
                                connectors = c_library.get_connectors(comp_type_b, comp_type_a, direction)
                                connector_id_a = connectors[0].id
                                connector_id_b = connectors[1].id

                                export["TOPOLOGY"][item]["CONNECTIONS"][
                                    component_b
                                ] = get_direction_from_components_and_connections(
                                    c_type_a, c_type_b, connector_id_b, connector_id_a
                                )
                            del export["TOPOLOGY"][component_b]["CONNECTIONS"][key]
                    to_delete.add(key)

            for key in to_delete:
                if key in export["TOPOLOGY"].keys():
                    # for comp, direction in export["TOPOLOGY"][key]["CONNECTIONS"].items():
                    # if comp != tracker[key]:
                    #     ctype_a_str = get_component_type_from_instance_name(key)
                    #     ctype_a = c_library.component_types[ctype_a_str]
                    #     ctype_b_str = get_component_type_from_instance_name(comp)
                    #     ctype_b = c_library.component_types[ctype_b_str]
                    #     connectors = c_library.get_connectors(ctype_a, ctype_b, direction)
                    #     connector_id_a = connectors[0].id
                    #     connector_id_b = connectors[1].id
                    #
                    #     export["TOPOLOGY"][comp]['CONNECTIONS'][tracker[key]] = get_direction_from_components_and_connections(
                    #         ctype_b.id, ctype_a.id, connector_id_b, connector_id_a
                    #     )
                    del export["TOPOLOGY"][key]
        return export
