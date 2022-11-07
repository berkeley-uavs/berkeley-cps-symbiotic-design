# type: ignore
import json

from sym_cps.representation.design.concrete import DConcrete
from sym_cps.representation.design.topology import DTopology
from sym_cps.representation.library import CConnector, CType, Library
from sym_cps.representation.tools.parsers.parsing_library import (
    all_parameters_lower_bounds,
    all_parameters_upper_bounds,
)
from sym_cps.shared.paths import library_folder
from sym_cps.tools.io import save_to_file
from sym_cps.tools.persistance import load
from sym_cps.tools.strings import repr_dictionary
from sym_cps.tools.update_library import update_dat_files_and_export
from tabulate import tabulate


def export_library(
        library_txt_file: str = "library.txt", library_dat_file: str = "library.dat",
        designs_dat_file: str = "designs.dat"
):
    """Export library and seed designs to text files"""

    c_library: Library = load(library_dat_file)  # type: ignore

    save_to_file(str(c_library), file_name=library_txt_file, absolute_folder_path=library_folder)

    """In the following we can see some of the 'temporary objects' that have been build 
        while building the components and designs libraries. We will save them to a text file in the output folder"""

    # Maps component type to all the LibraryComponent objects belonging to the type
    save_to_file(repr_dictionary(c_library.components_in_type), "all_components_in_type.txt", folder_name="library")

    # Maps each component type to a set of components type which it can be connected to"""
    connectable_components_types: dict[CType, set[CType]] = {}
    for ctype in c_library.component_types.values():
        connectable_components_types[ctype] = set(ctype.compatible_with.values())

    save_to_file(
        repr_dictionary(connectable_components_types), "connectable_components_types.txt", folder_name="library"
    )

    # Maps connector_id to its LibraryConnector object"""
    save_to_file(repr_dictionary(c_library.connectors), "all_connectors.txt", folder_name="library")

    # Maps connector to a set of 'compatible' connectors it can be connected to"""
    connectable_connectors: dict[CConnector, set[CConnector]] = {}
    for connector in c_library.connectors.values():
        connectable_connectors[connector] = set(connector.compatible_with.values())
    save_to_file(repr_dictionary(connectable_connectors), "connectable_connectors.txt", folder_name="library")

    # all_parameters_upper_bounds: dict[str, float] = {}
    # Maps parameter_id to its upper bounds"""
    save_to_file(repr_dictionary(all_parameters_upper_bounds), "all_parameters_upper_bounds.txt", folder_name="library")

    # all_parameters_lower_bounds: dict[str, float] = {}
    # Maps parameter_id to its lower bounds"""
    save_to_file(repr_dictionary(all_parameters_lower_bounds), "all_parameters_lower_bounds.txt", folder_name="library")

    # all_parameters: dict[str, CParameterType] = {}
    # Maps parameter_id to CParameterType object"""
    save_to_file(repr_dictionary(c_library.parameters), "all_parameters.txt", folder_name="library")

    # Maps parameter_id to a set of component types it belongs to"""
    parameter_to_components_types: dict[str, set[str]] = {}
    for para_id, parameter in c_library.parameters.items():
        if para_id not in parameter_to_components_types.keys():
            parameter_to_components_types[para_id] = set()
        parameter_to_components_types[para_id].add(parameter.belongs_to)

    save_to_file(
        repr_dictionary(parameter_to_components_types), "parameter_to_components_types.txt", folder_name="library"
    )

    designs: dict[str, tuple[DConcrete, DTopology]] = load(designs_dat_file)  # type: ignore

    for (d_concrete, d_topology) in designs.values():
        d_concrete.export_all()
        d_topology.export_all()


def analysis(library_dat_file: str = "library.dat", designs_dat_file: str = "designs.dat"):
    c_library: Library = load(library_dat_file)  # type: ignore

    all_types_in_library = set(c_library.component_types.keys())
    all_components_types_in_designs = set()
    shared_component_types_in_designs = set()

    components_types_in_design = {}
    component_used_in_designs = {}

    designs: dict[str, tuple[DConcrete, DTopology]] = load(designs_dat_file)  # type: ignore
    for design_id, (dconcrete, dtopology) in designs.items():
        component_types = set()
        for component in dconcrete.components:
            component_types.add(component.c_type.id)
            if component.c_type.id not in component_used_in_designs.keys():
                component_used_in_designs[component.c_type.id] = []
            if component.model not in component_used_in_designs[component.c_type.id]:
                component_used_in_designs[component.c_type.id].append(component.model)
        all_components_types_in_designs |= component_types
        if len(shared_component_types_in_designs) == 0:
            shared_component_types_in_designs |= component_types
        else:
            shared_component_types_in_designs = shared_component_types_in_designs.intersection(component_types)
        components_types_in_design[design_id] = list(component_types)

    unused_types = all_types_in_library - all_components_types_in_designs

    save_to_file("\n".join(list(all_components_types_in_designs)),
                 "component_types_in_seed_designs.txt",
                 folder_name="library"
                 )

    save_to_file("\n".join(list(unused_types)),
                 "unused_types.txt",
                 folder_name="library"
                 )

    types_in_use = {}
    for comp_type in all_components_types_in_designs:
        types_in_use[comp_type] = comp_type

    types_in_use_json = json.dumps(types_in_use, indent=4)

    save_to_file(types_in_use_json,
                 "types_renaming.json",
                 folder_name="library"
                 )

    components_types_in_design_json = json.dumps(components_types_in_design, indent=4)

    save_to_file(components_types_in_design_json,
                 "components_types_in_design.json",
                 folder_name="library"
                 )
    component_used_in_designs_json = json.dumps(component_used_in_designs, indent=4)
    save_to_file(component_used_in_designs_json,
                 "component_used_in_designs.json",
                 folder_name="library"
                 )


def generate_tables(library_dat_file: str = "library.dat"):
    c_library: Library = load(library_dat_file)  # type: ignore

    all_types_tables = []
    for component_type in c_library.component_types.values():
        c_type_table = []
        c_table_header = [component_type.id]
        for parameter in component_type.parameters.values():
            c_table_header.append(parameter.id)
        c_type_table.append(c_table_header)
        for component in c_library.components_in_type[component_type.id]:
            entry = [component.id]
            for parameter_id in c_table_header[1:]:
                entry.append(component.parameters[parameter_id].summary)
            c_type_table.append(entry)
        all_types_tables.append(c_type_table)

    for table in all_types_tables:
        print(table[0])


if __name__ == "__main__":
    update_dat_files_and_export()
    export_library()
