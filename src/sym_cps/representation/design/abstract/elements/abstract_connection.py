from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
from sym_cps.grammar import Direction
from sym_cps.representation.design.concrete import Connection, Component
from sym_cps.shared.library import c_library
from sym_cps.tools.strings import get_instance_name

if TYPE_CHECKING:
    from sym_cps.representation.design.abstract import AbstractComponent, Fuselage


@dataclass
class AbstractConnection:
    component_a: AbstractComponent
    component_b: AbstractComponent

    @property
    def type_id(self) -> str:
        ax, ay, az = self.component_a.grid_position
        bx, by, bz = self.component_b.grid_position
        connection_str = f"{ax}{ay}{az}{self.component_a.type_short_id}{bx}{by}{bz}{self.component_b.type_short_id}"
        return connection_str

    def to_concrete_connection(self) -> tuple[Connection, Connection]:
        ax, ay, az = self.component_a.grid_position
        bx, by, bz = self.component_b.grid_position

        tube = Component(
            id=get_instance_name("Tube", int(f"{ax}{ay}{az}{bx}{by}{bz}")),
            library_component=c_library.get_default_component("Tube"),
        )

        component_a = self.component_a.interface_component
        component_b = self.component_b.interface_component

        if self.direction_from_a_to_b == Direction.front:
            if component_a.c_type.id == "Hub4":
                """TODO check front side"""
                connector_a = c_library.connectors["Hub4__Side_Connector_1"]
            if component_a.c_type.id == "Flange":
                connector_a = c_library.connectors["Flange__SideConnector"]
            if component_b.c_type.id == "Hub4":
                """TODO check rear side"""
                connector_b = c_library.connectors["Hub4__Side_Connector_3"]
            if component_b.c_type.id == "Flange":
                connector_b = c_library.connectors["Flange__SideConnector"]
        elif self.direction_from_a_to_b == Direction.top:
            if component_a.c_type.id == "Hub4":
                connector_a = c_library.connectors["Hub4__Top_Connector"]
            if component_a.c_type.id == "Flange":
                connector_a = c_library.connectors["Flange__TopConnector"]
            if component_b.c_type.id == "Hub4":
                connector_b = c_library.connectors["Hub4__Bottom_Connector"]
            if component_b.c_type.id == "Flange":
                connector_b = c_library.connectors["Flange__BottomConnector"]
        else:
            """TODO: Complete"""

        connection_a_tube = Connection(component_a=component_a,
                                       connector_a=connector_a,
                                       component_b=tube,
                                       connector_b=c_library.connectors["Tube__BaseConnection"])

        connection_tube_b = Connection(component_a=tube,
                                       connector_a=c_library.connectors["Tube__EndConnection"],
                                       component_b=component_b,
                                       connector_b=connector_b)

        return connection_a_tube, connection_tube_b

    @property
    def key(self) -> str:
        a1 = self.component_a.id
        b1 = self.component_b.id
        if (a1) >= (b1):
            return f"{a1}-{b1}"
        return f"{b1}-{a1}"

    def __eq__(self, other: object):
        if not isinstance(other, AbstractConnection):
            return NotImplementedError
        return self.key == other.key

    def __hash__(self):
        return abs(hash(self.key))

    def __post_init__(self):
        self.component_a.add_connection(self)
        self.component_b.add_connection(self)

    @property
    def euclid_distance(self):
        position_a = self.component_a.grid_position
        position_b = self.component_b.grid_position
        point1 = np.array(position_a)
        point2 = np.array(position_b)
        return np.linalg.norm(point1 - point2)

    @property
    def direction_from_a_to_b(self) -> Direction:
        x, y, z = self.relative_position_from_a_to_b

        if y == 0 and z == 0:
            if x > 0:
                return Direction.front
            if x < 0:
                return Direction.rear
        if x == 0 and z == 0:
            if y > 0:
                return Direction.right
            if y < 0:
                return Direction.left
        if y == 0 and x == 0:
            if z > 0:
                return Direction.top
            if z < 0:
                return Direction.bottom
        raise Exception("ERROR in relative direction")

    @property
    def relative_position_from_a_to_b(self) -> tuple[int, int, int]:
        """returns the steps  (right(pos)/left(neg), top(pos)/bottom(neg))
        from component_a to _component_b"""

        position_a = self.component_a.grid_position
        position_b = self.component_b.grid_position

        # position_b.x - position_a.x
        # position_b.z - position_a.z

        rel_x = position_b[0] - position_a[0]
        rel_y = position_b[1] - position_a[1]
        rel_top = position_b[2] - position_a[2]

        return rel_x, rel_y, rel_top

    @property
    def relative_position_from_b_to_a(self) -> tuple[int, int, int]:
        """returns the steps  (right(pos)/left(neg), top(pos)/bottom(neg))
        from component_b to _component_a"""

        (rel_x, rel_y, rel_top) = self.relative_position_from_a_to_b

        return -rel_x, -rel_y, -rel_top
