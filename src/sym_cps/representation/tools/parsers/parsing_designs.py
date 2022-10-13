import json
import os
from pathlib import Path

from sym_cps.representation.design.concrete import DConcrete
from sym_cps.representation.design.concrete.elements.component import Component
from sym_cps.representation.design.concrete.elements.connection import Connection
from sym_cps.representation.design.concrete.elements.design_parameters import DesignParameter
from sym_cps.representation.design.concrete.elements.parameter import Parameter
from sym_cps.representation.design.topology import DTopology
from sym_cps.representation.library import Library
from sym_cps.representation.library.elements.c_connector import CConnector
from sym_cps.representation.tools.ids import connector_id, parameter_id
from sym_cps.representation.tools.parsers.temp_objects import (
    all_connectors,
    all_parameters,
    connectable_components_types,
    connectable_connectors,
)
from sym_cps.shared.paths import design_library_root_path_default


def parse_designs_from_folder(path: Path, library: Library) -> dict[str, tuple[DConcrete, DTopology]]:
    print(f"Parsing designs from {path}")

    dir_list = os.listdir(path=path)

    designs: dict[str, tuple[DConcrete, DTopology]] = {}

    for d in dir_list:
        design_path = os.path.join(design_library_root_path_default, d)
        print(f"Reading Design File: {design_path}")
        if os.path.isdir(design_path):

            dirname = os.path.basename(design_path)

            """Maps instance name to component name and to the parameters of the instance"""
            instance_component: dict[str, tuple[str, dict[str, tuple[float, str]]]] = {}

            """Maps instance name to the set of instance names connected to, for each connection we save the connectors names (from and to)"""
            instance_connection: dict[str, set[tuple[str, str, str]]] = {}

            with open(os.path.join(design_path, "info_componentMap3.json"), "r") as file:
                for elem in json.load(file):
                    instance_component[elem["FROM_COMP"]] = (
                        elem["LIB_COMPONENT"],
                        {},
                    )

            with open(os.path.join(design_path, "info_paramMap1.json"), "r") as file:

                for elem in json.load(file):
                    instance_component[elem["COMPONENT_NAME"]][1][elem["COMPONENT_PARAM"]] = (
                        float(elem["DESIGN_PARAM_VAL"]),
                        elem["DESIGN_PARAM"],
                    )
                    component_name = instance_component[elem["COMPONENT_NAME"]][0]
                    component_type = library.components[component_name].comp_type
                    # all_parameters[
                    #     parameter_id(elem["COMPONENT_PARAM"], str(component_type))
                    # ]._edit_field("design_parameter", elem["DESIGN_PARAM"])

            with open(os.path.join(design_path, "info_connectionMap2.json"), "r") as file:
                """Maps (instances, connectors) names to other (instances, connectors) names"""
                instance_connectors: list[dict[str, str]] = json.load(file)

            for entry in instance_connectors:

                try:
                    from_component_instance = entry["FROM_COMP"]
                    from_component_class = library.components[instance_component[entry["FROM_COMP"]][0]]
                except KeyError:
                    raise Exception(f"There is no component with named{instance_component[entry['FROM_COMP']]}")

                try:
                    to_component_instance = entry["TO_COMP"]
                    to_component_class = library.components[instance_component[entry["TO_COMP"]][0]]
                except KeyError:
                    raise Exception(f"There is no component with named{instance_component[entry['TO_COMP']]}")

                connector_id_from = connector_id(
                    name=entry["FROM_CONN"],
                    component_type=str(from_component_class.comp_type),
                )

                if connector_id_from not in all_connectors.keys():
                    # print(f"New connector found: {connector_id_from}")
                    all_connectors[connector_id_from] = CConnector(entry["FROM_CONN"], from_component_class.comp_type)

                connector_id_to = connector_id(
                    name=entry["TO_CONN"],
                    component_type=str(to_component_class.comp_type),
                )

                """Update component compatibility"""
                if from_component_class.comp_type in connectable_components_types.keys():
                    connectable_components_types[from_component_class.comp_type].add(to_component_class.comp_type)
                else:
                    connectable_components_types[from_component_class.comp_type] = {to_component_class.comp_type}

                """Update connectors compatibility"""
                if connector_id_from in connectable_connectors.keys():
                    connectable_connectors[connector_id_from].add(connector_id_to)
                else:
                    connectable_connectors[connector_id_from] = {connector_id_to}

                if connector_id_to not in all_connectors.keys():
                    # print(f"New connector found: {connector_id_to}")
                    all_connectors[connector_id_to] = CConnector(entry["TO_CONN"], to_component_class.comp_type)

                if from_component_instance in instance_connection.keys():
                    instance_connection[from_component_instance].add(
                        (to_component_instance, connector_id_from, connector_id_to)
                    )
                else:
                    instance_connection[from_component_instance] = {
                        (to_component_instance, connector_id_from, connector_id_to)
                    }

            """Create new DConcrete"""
            new_design = DConcrete(name=dirname)
            for instance, (
                component,
                parameters_floats,
            ) in instance_component.items():
                parameters: dict[str, Parameter] = {}
                new_component = Component(
                    id=instance,
                    library_component=library.components[component],
                    parameters=parameters,
                )
                for name, (value, design_parameter) in parameters_floats.items():
                    param_id = parameter_id(name, str(library.components[component].comp_type))
                    param_type = all_parameters[param_id]
                    print(f"value: {value}")
                    print(f"component: {new_component}")
                    print(f"type: {param_type}")
                    parameter = Parameter(value, param_type, new_component)
                    parameters[param_id] = parameter
                    if id(parameters[param_id]) != id(parameter):
                        print("ERROR")
                    if design_parameter in new_design.design_parameters.keys():
                        new_design.design_parameters[design_parameter].add(parameter)
                    else:
                        new_design.design_parameters[design_parameter] = DesignParameter(
                            id=design_parameter, parameters={parameter}
                        )
                        # if id(parameter) in [id(p) for p in  new_design.design_parameters[design_parameter].parameters]:
                        #     print(f"{id(parameter)}")
                new_component._edit_field("parameters", parameters)
                for pid, para_a in new_component.parameters.items():
                    for value in new_design.design_parameters.values():
                        for p in value.parameters:
                            if str(p) == str(para_a):
                                if id(para_a) != id(p):
                                    print(
                                        f"{p.c_parameter.id} in component {new_component.id} has"
                                        f"a different object in design_parameter {value.id}\\"
                                        f"{id(para_a)} != {id(p)}\n"
                                        f"{str(para_a)}\n"
                                        f"{str(p)}\n\n"
                                    )
                new_design.add_node(new_component)

            connections_set = []
            for instance_s, connections in instance_connection.items():
                for (instance_t, connector_s, connector_t) in connections:
                    # print(f"{instance_s}, {connector_s}, {instance_t}, {connector_t}")
                    connection = Connection(
                        component_a=new_design.get_instance(instance_s),
                        connector_a=all_connectors[connector_s],
                        component_b=new_design.get_instance(instance_t),
                        connector_b=all_connectors[connector_t],
                    )
                    connections_set.append(connection)
            # TODO: Bugfix: new_design.get_istance(instance_s) sometimes is None
            try:
                for connection in connections_set:
                    new_design.connect(connection)
            except:
                raise Exception("ERROR")

            d_concrete = new_design
            d_topology = DTopology.from_concrete(new_design)
            designs[new_design.name] = (d_concrete, d_topology)

    for key, value in connectable_connectors.items():
        for output_connector in value:  # type: ignore
            # print(f"{key} -> {output_connector}")
            all_connectors[key]._update_field(
                "compatible_with",
                {all_connectors[output_connector].id: all_connectors[output_connector]},
            )

    return designs


def parse_design_from_design_swri(path: Path, library: Library) -> DConcrete:
    """Initialize a DConcrete from a design_swri file data"""
    """Read design_swri file"""
    with open(path, "r") as design_swri_file:
        design_swri_data = json.load(design_swri_file)
    """Read the design name"""
    design_name = design_swri_data["name"]
    new_design = DConcrete(name=design_name)
    """Read the components and parameters"""
    # maps component instance name to library component
    component_map: dict[str, tuple[str, dict[str, Parameter]]] = {}
    for component_data in design_swri_data["components"]:
        component_instance_str = component_data["component_instance"]
        library_component_str = component_data["component_choice"]
        component_map[component_instance_str] = (library_component_str, {})

    for parameter_data in design_swri_data["parameters"]:
        parameter_name = parameter_data["parameter_name"]
        parameter_value = parameter_data["value"]
        component_properties = parameter_data["component_properties"]
        parameters: dict[str, Parameter] = {}
        for prop in component_properties:
            component_name = prop["component_name"]
            component_property = prop["component_property"]
            library_component_str = component_map[component_name][0]
            param_id = parameter_id(component_property, library.components[library_component_str].comp_type.id)

            for p, para in library.parameters.items():
                print(p)
            try:
                param_type = library.parameters[param_id]
            except:
                print("wasda")
            param_type = library.parameters[param_id]
            parameter = Parameter(parameter_value, param_type)
            parameters[param_id] = parameter
            component_map[component_name][1][param_id] = parameter

        for p in parameters.values():
            if isinstance(p.component, str):
                print("ERRORRRR")
        new_design.design_parameters[parameter_name] = DesignParameter(
            id=parameter_name, parameters=set(parameters.values())
        )

    for component_name, (library_component_str, parameters) in component_map.items():
        new_component = Component(
            id=component_name,
            library_component=library.components[library_component_str],
            parameters=parameters,
        )
        new_design.add_node(new_component)
    """Read the connection"""
    for connection_data in design_swri_data["connections"]:
        instance_s = connection_data["from_ci"]
        instance_t = connection_data["to_ci"]
        component_choice_s = component_map[instance_s][0]
        component_choice_t = component_map[instance_t][0]
        connector_id_s = connector_id(
            name=connection_data["from_conn"],
            component_type=str(library.components[component_choice_s].comp_type),
        )
        connector_id_t = connector_id(
            name=connection_data["to_conn"],
            component_type=str(library.components[component_choice_t].comp_type),
        )
        connection = Connection(
            component_a=new_design.get_instance(instance_s),
            connector_a=library.connectors[connector_id_s],
            component_b=new_design.get_instance(instance_t),
            connector_b=library.connectors[connector_id_t],
        )
        try:
            new_design.connect(connection)
        except:
            pass
    # d_concrete = new_design
    # d_topology = DTopology.from_concrete(new_design)
    """TODO: Update connectable connectors"""
    # for key, value in connectable_connectors.items():
    #    for output_connector in value: # type: ignore
    #        # print(f"{key} -> {output_connector}")
    #        all_connectors[key]._update_field("compatible_with", {all_connectors[output_connector].id: all_connectors[output_connector]})
    return new_design
