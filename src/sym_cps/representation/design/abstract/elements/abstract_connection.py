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

    def get_connector(self, c_type: str, direction: str):
        """Returns CConnector based on ctype and directions.
        (flange cannot connect to a tube from the top because only motor can connect to top)"""

        connectors_map = {
            "Hub4": {
                Direction.front: "Hub4__Side_Connector_2",
                Direction.rear: "Hub4__Side_Connector_4",
                Direction.left: "Hub4__Side_Connector_1",
                Direction.right: "Hub4__Side_Connector_3",
                Direction.top: "Hub4__Top_Connector",
                Direction.bottom: "Hub4__Bottom_Connector"
            },
            "Flange": {
                Direction.front: "Flange__SideConnector",
                Direction.rear: "Flange__SideConnector",
                Direction.left: "Flange__SideConnector",
                Direction.right: "Flange__SideConnector",
                Direction.top: "Flange__BottomConnector",
                Direction.bottom: "Flange__BottomConnector"
            },
        }
        connector = connectors_map[c_type][direction]
        return c_library.connectors[connector]

    def to_concrete_connection(self) -> tuple[Connection, Connection]:
        ax, ay, az = self.component_a.grid_position
        bx, by, bz = self.component_b.grid_position

        tube = Component(
            id=get_instance_name("Tube", int(f"{ax}{ay}{az}{bx}{by}{bz}")),
            library_component=c_library.get_default_component("Tube"),
        )

        component_a = self.component_a.interface_component
        component_b = self.component_b.interface_component

        connector_a = self.get_connector(component_a.c_type.id, self.direction_from_a_to_b)
        connector_b = self.get_connector(component_b.c_type.id, self.direction_from_b_to_a)

        bottom_tube_connector = c_library.connectors["Tube__BaseConnection"]
        top_tube_connector = c_library.connectors["Tube__EndConnection"]

        if self.direction_from_a_to_b == Direction.top or self.direction_from_a_to_b == Direction.bottom:
            bottom_tube_connector = c_library.connectors["Tube__OffsetConnection2"]
            top_tube_connector = c_library.connectors["Tube__OffsetConnection1"]

        connection_a_tube = Connection(component_a=component_a,
                                       connector_a=connector_a,
                                       component_b=tube,
                                       connector_b=bottom_tube_connector)

        connection_tube_b = Connection(component_a=tube,
                                       connector_a=top_tube_connector,
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
                return Direction.left
            if x < 0:
                return Direction.right
        if x == 0 and z == 0:
            if y > 0:
                return Direction.rear
            if y < 0:
                return Direction.front
        if y == 0 and x == 0:
            if z > 0:
                return Direction.top
            if z < 0:
                return Direction.bottom
        raise Exception("ERROR in relative direction")

    @property
    def direction_from_b_to_a(self) -> Direction:
        x, y, z = self.relative_position_from_b_to_a

        if y == 0 and z == 0:
            if x > 0:
                return Direction.left
            if x < 0:
                return Direction.right
        if x == 0 and z == 0:
            if y > 0:
                return Direction.rear
            if y < 0:
                return Direction.front
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
