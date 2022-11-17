from __future__ import annotations

import abc
import json
from dataclasses import dataclass, field

import numpy as np
from sym_cps.grammar.rules import generate_random_topology, Grid
from sym_cps.shared.paths import grammar_rules_path

rule_dict = json.load(open(grammar_rules_path))


@dataclass
class AbstractComponent(abc.ABC):
    grid_position: tuple[int, int, int]
    base_name: str = ""
    id: str = ""
    connections: set[AbstractConnection] = field(default_factory=set)
    parameters: {} = field(default_factory=dict)

    def add_connection(self, abstract_connection: AbstractConnection):
        self.connections.add(abstract_connection)


@dataclass
class Fuselage(AbstractComponent):
    instance_n: int = 1

    def __post_init__(self):
        self.base_name = "Fuselage_str"
        self.instance_id = f"Fuselage_str_instance_{self.instance_n}"


@dataclass
class Propeller(AbstractComponent):
    instance_n: int = 1

    def __post_init__(self):
        self.base_name = "Propeller_str"
        self.instance_id = f"Propeller_str_instance_{self.instance_n}"


@dataclass
class Wing(AbstractComponent):
    instance_n: int = 1

    def __post_init__(self):
        self.base_name = "Wing"
        self.instance_id = f"Wing_instance_{self.instance_n}"


@dataclass
class Connector(AbstractComponent):
    instance_n: int = 1

    def __post_init__(self):
        self.base_name = "Connector"
        self.instance_id = f"Connector_instance_{self.instance_n}"


@dataclass
class Tube(AbstractComponent):
    instance_n: int = 1

    def __post_init__(self):
        self.base_name = "Tube"
        self.instance_id = f"Tube_instance_{self.instance_n}"


@dataclass
class Hub(AbstractComponent):
    instance_n: int = 1

    def __post_init__(self):
        self.base_name = "Hub"
        self.instance_id = f"Hub_instance_{self.instance_n}"


@dataclass
class AbstractConnection:
    component_a: AbstractComponent
    component_b: AbstractComponent

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
    def relative_position_from_a_to_b(self, ) -> [int, int]:
        """returns the steps  (right(pos)/left(neg), top(pos)/bottom(neg))
        from component_a to _component_b"""

        position_a = self.component_a.grid_position
        position_b = self.component_b.grid_position
        point1 = np.array(position_a)
        point2 = np.array(position_b)

        #TODO

        return np.linalg.norm(point1 - point2)

    @property
    def relative_position_from_b_to_a(self, ) -> [int, int]:
        """returns the steps  (right(pos)/left(neg), top(pos)/bottom(neg))
        from component_b to _component_a"""

        position_a = self.component_a.grid_position
        position_b = self.component_b.grid_position
        point1 = np.array(position_a)
        point2 = np.array(position_b)

        #TODO


        return np.linalg.norm(point1 - point2)


@dataclass
class AbstractDesign:
    grid: dict[tuple, AbstractComponent] = field(default_factory=dict)
    connections: set[AbstractConnection] = field(default_factory=set)

    def add_abstract_component(self, position: tuple[int, int, int], component: AbstractComponent):
        c_instance_n = 1
        for e in self.grid.values():
            if isinstance(e, component.__class__):
                c_instance_n += 1
        component.id = c_instance_n
        self.grid[position] = component

    def add_connection(self, position_a: tuple[int, int, int], position_b: tuple[int, int, int]):
        abstract_component_a = self.grid[position_a]
        abstract_component_b = self.grid[position_b]
        abstract_connection = AbstractConnection(abstract_component_a, abstract_component_b)
        self.connections.add(abstract_connection)

    def parse_grid(self, grid: Grid):
        nodes = grid.nodes
        self.grid_size = len(nodes)

        for x_pos, x_axis in enumerate(nodes):
            for y_pos, y_axis in enumerate(x_axis):
                for z_pos, node_element in enumerate(y_axis):
                    position = (x_pos, y_pos, z_pos)
                    if node_element == "FUSELAGE":
                        self.add_abstract_component(position, Fuselage(grid_position=position))
                    if "WING" in node_element:
                        self.add_abstract_component(position, Wing(grid_position=position))
                    if "ROTOR" in node_element:
                        self.add_abstract_component(position, Propeller(grid_position=position))
                    if "CONNECTOR" in node_element:
                        self.add_abstract_component(position, Connector(grid_position=position))

        for position_a, connections in grid.adjacencies.items():
            for position_b in connections:
                self.add_connection(position_a, position_b)


if __name__ == '__main__':
    new_design = AbstractDesign()
    new_design.parse_grid(generate_random_topology())
    print(new_design.grid)
