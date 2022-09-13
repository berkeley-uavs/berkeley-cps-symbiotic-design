import json
import os
from pathlib import Path

from sym_cps.representation.library import Library
from sym_cps.representation.library.elements.c_connector import CConnector
from sym_cps.representation.library.elements.c_type import CType
from sym_cps.shared.paths import design_library_root_path_default
from sym_cps.representation.tools.ids import connector_id, parameter_id


def parse_connections_and_parameters_from_designs(path: Path, library: Library):
    print(f"Parsing designs from {path}")

    dir_list = os.listdir(path=path)

    """Learned dictionaries from design"""
    design_parameters: dict[str, str] = {}
    # Maps each component class to a set of components class which it can be connected to"""
    connectable_components_types: dict[CType, set[CType]] = {}
    # Maps all connector_ids to Connector objects"""
    all_connectors: dict[str, CConnector] = {}
    # Maps all connector_ids to a set of connector_ids it is connectable with"""
    connectable_connectors: dict[str, set[CConnector]] = {}

    for d in dir_list:
        design_path = os.path.join(design_library_root_path_default, d)
        print(f"Reading Design File: {design_path}")
        if os.path.isdir(design_path):

            """Maps instance name to component name and to the parameters of the instance"""
            instance_component: dict[str, tuple[str, dict[str, tuple[float, str]]]] = {}

            with open(
                os.path.join(design_path, "info_componentMap3.json"), "r"
            ) as file:
                for elem in json.load(file):
                    instance_component[elem["FROM_COMP"]] = (
                        elem["LIB_COMPONENT"],
                        {},
                    )

            with open(os.path.join(design_path, "info_paramMap1.json"), "r") as file:

                for elem in json.load(file):
                    instance_component[elem["COMPONENT_NAME"]][1][
                        elem["COMPONENT_PARAM"]
                    ] = (float(elem["DESIGN_PARAM_VAL"]), elem["DESIGN_PARAM"])
                    component_name = instance_component[elem["COMPONENT_NAME"]][0]
                    component_type = library.components[component_name].comp_type
                    design_parameters[
                        parameter_id(elem["COMPONENT_PARAM"], str(component_type))
                    ] = elem["DESIGN_PARAM"]

            with open(
                os.path.join(design_path, "info_connectionMap2.json"), "r"
            ) as file:
                """Maps (instances, connectors) names to other (instances, connectors) names"""
                instance_connectors: list[dict[str, str]] = json.load(file)

            for entry in instance_connectors:

                try:
                    from_component_instance = entry["FROM_COMP"]
                    from_component_class = library.components[
                        instance_component[entry["FROM_COMP"]][0]
                    ]
                except KeyError:
                    raise Exception(
                        f"There is no component with named{instance_component[entry['FROM_COMP']]}"
                    )

                try:
                    to_component_instance = entry["TO_COMP"]
                    to_component_class = library.components[
                        instance_component[entry["TO_COMP"]][0]
                    ]
                except KeyError:
                    raise Exception(
                        f"There is no component with named{instance_component[entry['TO_COMP']]}"
                    )

                connector_id_from = connector_id(
                    name=entry["FROM_CONN"],
                    component_type=str(from_component_class.comp_type),
                )

                if connector_id_from not in all_connectors.keys():
                    # print(f"New connector found: {connector_id_from}")
                    all_connectors[connector_id_from] = CConnector(
                        entry["FROM_CONN"], from_component_class.comp_type
                    )

                connector_id_to = connector_id(
                    name=entry["TO_CONN"],
                    component_type=str(to_component_class.comp_type),
                )

                """Update component compatibility"""
                if (
                    from_component_class.comp_type
                    in connectable_components_types.keys()
                ):
                    connectable_components_types[from_component_class.comp_type].add(
                        to_component_class.comp_type
                    )
                else:
                    connectable_components_types[from_component_class.comp_type] = {
                        to_component_class.comp_type
                    }

                # print(library.connectors.keys())
                # print("WAIT")
                """Update connectors compatibility"""
                if connector_id_from in connectable_connectors.keys():
                    connectable_connectors[connector_id_from].add(
                        library.connectors[connector_id_to]
                    )
                else:
                    if connector_id_to not in library.connectors.keys():
                        print(f"{connector_id_to} missing")
                    else:
                        connectable_connectors[connector_id_from] = {
                            library.connectors[connector_id_to]
                        }

                if connector_id_to not in all_connectors.keys():
                    # print(f"New connector found: {connector_id_to}")
                    all_connectors[connector_id_to] = CConnector(
                        entry["TO_CONN"], to_component_class.comp_type
                    )

    return connectable_connectors, connectable_components_types, design_parameters


def update_connections_and_parameters_compatibility(
    connectable_connectors: dict[str, set[str]] | None,
    connectable_components_types: dict[CType, set[CType]] | None,
    design_parameters: dict[str, str] | None,
    library: Library,
):
    if isinstance(connectable_connectors, dict):
        for key, value in connectable_connectors.items():
            for output_connector in value:  # type: ignore
                if output_connector.id in library.connectors.keys():
                    # print(f"{key} -> {output_connector}")
                    library.connectors[key]._update_field(
                        "compatible_with", {output_connector.id: output_connector}
                    )

    if isinstance(connectable_components_types, dict):
        for key, value in connectable_components_types.items():
            for compatible_class in value:  # type: ignore
                library.component_types[key.id]._update_field(
                    "compatible_with", {compatible_class.id: compatible_class}
                )

    if isinstance(design_parameters, dict):
        for key, value in design_parameters.items():
            library.parameters[key]._edit_field("design_parameter", value)
