from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sym_cps.grammar.tools import get_direction_from_components_and_connections
from sym_cps.shared.objects import connections_map

if TYPE_CHECKING:
    from sym_cps.representation.design.concrete.elements.component import Component
    from sym_cps.representation.library.elements.c_connector import CConnector


@dataclass(frozen=True)
class Connection:
    """Models the connection between two 'Component'.
    Each Connection is symmetric, i.e. Connection(A,B) = Connection(B,A)"""

    component_a: Component
    connector_a: CConnector
    component_b: Component
    connector_b: CConnector
    # brendan: make api to output connector_a and connect_b given component_a and component_b

    @classmethod
    def from_direction(cls, component_a: Component, component_b: Component, direction: str):

        print(f"connecting {component_a.c_type.id} to {component_b.c_type.id}, direction: {direction}")
        connector_a = connections_map[component_a.c_type.id][component_b.c_type.id][direction][0]
        connector_b = connections_map[component_a.c_type.id][component_b.c_type.id][direction][1]
        from sym_cps.shared.library import c_library

        print(f"use {connector_a} - {connector_b}")
        return cls(
            component_a,
            c_library.connectors[connector_a],
            component_b,
            c_library.connectors[connector_b],
        )

    @property
    def components_and_connectors(self) -> set[tuple[Component, CConnector]]:
        """Returns a set of two tuples, where each tuple is formed by a Component and a CConnector"""

        connections = set()
        connections.add((self.component_a, self.connector_a))
        connections.add((self.component_b, self.connector_b))
        return connections

    @property
    def components(self) -> tuple[Component, Component]:
        """Returns the two components connected"""

        return self.component_a, self.component_b

    @property
    def summary(self) -> dict:
        return {self.component_a.id: self.connector_a.id, self.component_b.id: self.connector_b.id}

    @property
    def key(self) -> str:
        a1 = self.component_a.id
        a2 = self.connector_a.id
        b1 = self.component_b.id
        b2 = self.connector_b.id

        if (a1 + a2) >= (b1 + b2):
            return f"{a1}-{a2}-{b1}-{b2}"
        return f"{b1}-{b2}-{a1}-{a2}"

    @property
    def lib_key(self) -> str:
        a1 = self.component_a.library_component.id
        a2 = self.connector_a.id
        b1 = self.component_b.library_component.id
        b2 = self.connector_b.id

        return f"{a1}-{a2}-{b1}-{b2}"

        # if (a1 + a2) >= (b1 + b2):
        #     return f"{a1}-{a2}-{b1}-{b2}"
        # return f"{b1}-{b2}-{a1}-{a2}"

    @property
    def direction_b_respect_to_a(self):
        return get_direction_from_components_and_connections(
            self.component_a.c_type.id, self.component_b.c_type.id, self.connector_a.id, self.connector_b.id
        )

    def __eq__(self, other: object):
        if not isinstance(other, Connection):
            return NotImplementedError

        return self.key == other.key

    def is_similar(self, other: Connection):
        return self.lib_key == other.lib_key

    def __ne__(self, other: object):
        if not isinstance(other, Connection):
            return NotImplementedError

        return not self.__eq__(other)

    def __str__(self):

        s1 = (
            f"FROM\n\tCOMPONENT\t{self.component_a.c_type.id} ({self.component_a.id})"
            f"\n\tCONNECTOR\t{self.connector_a.name}\n"
        )
        s2 = (
            f"TO\n\tCOMPONENT\t{self.component_b.c_type.id} ({self.component_b.id})"
            f"\n\tCONNECTOR\t{self.connector_b.name}\n"
        )
        return f"{s1}{s2}"

    def __hash__(self):
        return abs(hash(self.key))
