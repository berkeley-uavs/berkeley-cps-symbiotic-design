# type: ignore
from sym_cps.representation.tools.parsers.learn_from_designs import parse_connections_and_parameters_from_designs
from sym_cps.representation.tools.parsers.parsing_designs import parse_designs_from_folder
from sym_cps.shared.paths import component_library_root_path_default, design_library_root_path_default

from sym_cps.representation.design.concrete import DConcrete
from sym_cps.representation.design.topology import DTopology
from sym_cps.representation.library import Library


def parse_library_and_seed_designs() -> tuple[Library, dict[str, tuple[DConcrete, DTopology]]]:
    from sym_cps.representation.library import Library
    """Generates a Components Library"""
    c_library: Library = Library().from_folder(path=component_library_root_path_default)

    """Learn information form existing designs"""
    (
        connectable_connectors,
        connectable_components_types,
        design_parameters,
    ) = parse_connections_and_parameters_from_designs(design_library_root_path_default, library=c_library)

    """Update information to the library"""
    c_library.update_information(connectable_connectors, connectable_components_types, design_parameters)

    """Load Seed Designs"""
    designs = parse_designs_from_folder(design_library_root_path_default, library=c_library)

    return c_library, designs
