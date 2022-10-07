from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

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

    def __post_init__(self):
        """TODO: is connection legal?"""

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
    def key(self) -> str:
        a1 = self.component_a.id
        a2 = self.connector_a.id
        b1 = self.component_b.id
        b2 = self.connector_b.id

        if (a1 + a2) >= (b1 + b2):
            return f"{a1}-{a2}-{b1}-{b2}"
        return f"{b1}-{b2}-{a1}-{a2}"

    def __eq__(self, other: object):
        if not isinstance(other, Connection):
            return NotImplementedError

        return self.key == other.key

    def __ne__(self, other: object):
        if not isinstance(other, Connection):
            return NotImplementedError

        return not self.__eq__(other)

    def __str__(self):

        s1 = f"FROM\n\tCOMPONENT\t{self.component_a.c_type.id} ({self.component_a.id})" \
             f"\n\tCONNECTOR\t{self.connector_a.name}\n"
        s2 = f"TO\n\tCOMPONENT\t{self.component_b.c_type.id} ({self.component_b.id})" \
             f"\n\tCONNECTOR\t{self.connector_b.name}\n"
        return f"{s1}{s2}"

    def __hash__(self):
        return abs(hash(self.key))
