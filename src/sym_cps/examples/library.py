# type: ignore
from sym_cps.representation.design.concrete import DConcrete
from sym_cps.representation.design.topology import DTopology
from sym_cps.representation.library import Library, CType, CConnector
from sym_cps.representation.tools.parsers.parse import parse_library_and_seed_designs
from sym_cps.representation.tools.parsers.parsing_library import all_parameters_upper_bounds, \
    all_parameters_lower_bounds
from sym_cps.shared.paths import library_folder, designs_folder, ExportType
from sym_cps.tools.io import save_to_file
from sym_cps.tools.persistance import dump, load
from sym_cps.tools.strings import repr_dictionary


def parse_library(library_dat_file: str = "library.dat", designs_dat_file: str = "designs.dat"):
    """Loads library of components and seed designs and store them"""

    c_library, designs = parse_library_and_seed_designs()
    dump(c_library, library_dat_file)
    dump(designs, designs_dat_file)


def export_library(library_txt_file: str = "library.txt",
                   library_dat_file: str = "library.dat",
                   designs_dat_file: str = "designs.dat"):
    """Export library and seed designs to text files"""

    c_library: Library = load(library_dat_file)  # type: ignore

    save_to_file(str(c_library),
                 file_name=library_txt_file,
                 absolute_folder_path=library_folder)

    """In the following we can see some of the 'temporary objects' that have been build 
        while building the components and designs libraries. We will save them to a text file in the output folder"""

    # Maps component type to all the LibraryComponent objects belonging to the type
    save_to_file(
        repr_dictionary(c_library.components_in_type), "all_components_in_type.txt", folder_name="library"
    )

    # Maps each component type to a set of components type which it can be connected to"""
    connectable_components_types: dict[CType, set[CType]] = {}
    for ctype in c_library.component_types.values():
        connectable_components_types[ctype] = set(ctype.compatible_with.values())

    save_to_file(
        repr_dictionary(connectable_components_types),
        "connectable_components_types.txt", folder_name="library"
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
    save_to_file(
        repr_dictionary(all_parameters_upper_bounds), "all_parameters_upper_bounds.txt", folder_name="library"
    )

    # all_parameters_lower_bounds: dict[str, float] = {}
    # Maps parameter_id to its lower bounds"""
    save_to_file(
        repr_dictionary(all_parameters_lower_bounds), "all_parameters_lower_bounds.txt", folder_name="library"
    )

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

    for d_concrete, d_topology in designs.values():
        d_concrete.export(ExportType.JSON)
        save_to_file(
            str(d_concrete),
            file_name=f"DConcrete",
            absolute_folder_path=designs_folder / d_concrete.name,
        )
        save_to_file(
            str(d_topology),
            file_name=f"DTopology",
            absolute_folder_path=designs_folder / d_concrete.name,
        )
        d_topology.export(ExportType.DOT)
        save_to_file(
            str(d_concrete.generate_connections_json()),
            file_name=f"connections.json",
            absolute_folder_path=designs_folder / d_concrete.name,
        )
        print("terminated")


if __name__ == '__main__':
    parse_library()
    export_library()
