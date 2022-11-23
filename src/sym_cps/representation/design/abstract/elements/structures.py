from __future__ import annotations

from dataclasses import dataclass

from sym_cps.representation.library import CParameter, LibraryComponent


@dataclass
class GenericConnection:
    component_a: LibraryComponent
    component_b: LibraryComponent
    direction: str


@dataclass
class GenericComponent:
    library_component: LibraryComponent
    connections: set[GenericConnection]
    parameters: dict[CParameter, float]


@dataclass
class Structure:
    name: str
    components: set[GenericComponent]
