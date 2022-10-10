from __future__ import annotations

from enum import Enum, auto

from sym_cps.representation.library import CType


class Direction(Enum):
    TOP = auto()
    BOTTOM = auto()
    INSIDE = auto()


def connect(component_type_a: str, component_b: str,
            lib_component_b: str,
            direction: Direction) -> [(str, str)]:
    if lib_component_a == "capsule_fuselage" and \
            lib_component_b == "main_hub" and \
            direction == Direction.BOTTOM:
        return "capsule_fuselage__BottomConnector"
