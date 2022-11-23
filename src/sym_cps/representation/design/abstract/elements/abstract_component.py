from __future__ import annotations

from dataclasses import dataclass, field

from sym_cps.representation.design.abstract import AbstractConnection
from sym_cps.representation.design.abstract.elements.structures import Structure

from sym_cps.representation.design.concrete import Component
from sym_cps.tools.strings import get_instance_name


@dataclass
class AbstractComponent:
    """
    Element of a 3D grid. A structure of multiple 'Component'
    """
    grid_position: tuple[int, int, int]
    base_name: str = ""
    instance_n: int = 1
    connections: set[AbstractConnection] = field(default_factory=set)
    color: str = "black"
    structure: set[Component] = field(default_factory=set)

    def add_connection(self, abstract_connection: AbstractConnection):
        self.connections.add(abstract_connection)

    @property
    def id(self) -> str:
        return get_instance_name(self.base_name, self.instance_n)

    @property
    def export(self) -> dict:
        return {self.id: {"position": self.grid_position, "connections": [e.component_b.id for e in self.connections]}}


@dataclass
class Fuselage(AbstractComponent):
    instance_n: int = 1

    def __post_init__(self):
        self.base_name = "Fuselage_str"
        self.color = "red"
        """TODO: add Components in the fuselage structure with their parameters"""




    def __hash__(self):
        return hash(self.id)


@dataclass
class Propeller(AbstractComponent):
    instance_n: int = 1

    def __post_init__(self):
        self.base_name = "Propeller_str"
        self.color = "green"

    def __hash__(self):
        return hash(self.id)


@dataclass
class Wing(AbstractComponent):
    instance_n: int = 1

    def __post_init__(self):
        self.base_name = "Wing"
        self.color = "blue"

    def __hash__(self):
        return hash(self.id)


@dataclass
class Connector(AbstractComponent):
    instance_n: int = 1

    def __post_init__(self):
        self.base_name = "Connector"
        self.color = "gray"

    def __hash__(self):
        return hash(self.id)


@dataclass
class Tube(AbstractComponent):
    euclid_distance: int = 1
    instance_n: int = 1

    def __post_init__(self):
        self.base_name = "Tube"

    def __hash__(self):
        return hash(self.id)


@dataclass
class Hub(AbstractComponent):
    instance_n: int = 1

    def __post_init__(self):
        self.base_name = "Hub"

    def __hash__(self):
        return hash(self.id)
