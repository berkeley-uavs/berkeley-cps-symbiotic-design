from __future__ import annotations

from enum import Enum, auto

from sym_cps.representation.library import CConnector


class Direction(Enum):
    TOP = auto()
    BOTTOM = auto()
    LEFT = auto()
    INSIDE = auto()




def connect(lib_component_a: str,
            lib_component_b: str,
            direction: Direction) -> [(str, str)]:
    if lib_component_a == "capsule_fuselage" and \
            lib_component_b == "main_hub" and \
            direction == Direction.BOTTOM:
        return "capsule_fuselage__BottomConnector"
