from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from sym_cps.representation.design.abstract.elements import AbstractComponent
from sym_cps.representation.library import LibraryComponent, CParameter


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

