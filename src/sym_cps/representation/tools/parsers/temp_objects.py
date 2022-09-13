from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sym_cps.representation.design.concrete import DConcrete
    from sym_cps.representation.library.elements.c_connector import CConnector
    from sym_cps.representation.library.elements.c_parameter import CParameter
    from sym_cps.representation.library.elements.library_component import (
        CType,
        LibraryComponent,
    )


# Maps components name to LibraryComponent objects
all_library_components: dict[str, LibraryComponent] = {}

# All component types
all_component_types: dict[str, CType] = {}

# Maps component types to all the LibraryComponent objects in the type
all_components_in_type: dict[str, set[LibraryComponent]] = {}

# Maps each component type to a set of components type which it can be connected to"""
connectable_components_types: dict[CType, set[CType]] = {}

# Maps all connector_ids to Connector objects"""
all_connectors: dict[str, CConnector] = {}

# Maps all connector_ids to a set of connector_ids it is connectable with"""
connectable_connectors: dict[str, set[str]] = {}

# Maps all parameter_ids to ParameterType objects"""
all_parameters: dict[str, CParameter] = {}

# Maps all parameter_ids to a set of component types they belong ot"""
parameter_to_components: dict[str, set[str]] = {}

# Set of seed designs"""
seed_designs: set[DConcrete] = set()

# # External Configuration file
# configs = Dynaconf(
#     envvar_prefix="DYNACONF",
#     settings_files=[Path(f'{configuration_files_path}/current.toml')]
# )
