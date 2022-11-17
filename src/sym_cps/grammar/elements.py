from __future__ import annotations

import abc
import json
from dataclasses import dataclass, field

import numpy as np
from sym_cps.shared.paths import grammar_rules_path

rule_dict = json.load(open(grammar_rules_path))



@dataclass
class Grid:
    nodes: list[list[list[str]]]
    adjacencies: dict[tuple, list[tuple]]


@dataclass
class AbstractComponent(abc.ABC):
    base_name: str = ""
    instance_id: str = ""
    connections: {} = field(default_factory=dict)
    parameters: {} = field(default_factory=dict)

    def connected_with(self, other: AbstractComponent, euclid_distance: float):
        self.connections[other] = euclid_distance


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
    elements: tuple[AbstractComponent, AbstractComponent, int]


@dataclass
class AbstractDesign:
    grid: dict[tuple, AbstractComponent] = field(default_factory=dict)
    connections: list[AbstractConnection] = field(default_factory=list)

    def add_abstract_component(self, position: tuple[int, int, int], component: AbstractComponent):
        c_instance_n = 1
        for e in self.grid.values():
            if isinstance(e, component.__class__):
                c_instance_n += 1
        component.instance_id = c_instance_n
        self.grid[position] = component

    def add_connection(self, position_a: tuple[int, int, int], position_b: tuple[int, int, int]):

        point1 = np.array(position_a)
        point2 = np.array(position_b)
        dist = np.linalg.norm(point1 - point2)

        self.grid[position_a].connected_with(self.grid[position_b], dist)
        # TODO

    def parse_grid(self, grid: Grid):
        nodes = grid.nodes

        for x_pos, x_axis in enumerate(nodes):
            for y_pos, y_axis in enumerate(x_axis):
                for z_pos, node_element in enumerate(y_axis):
                    position = (x_pos, y_pos, z_pos)
                    if node_element == "FUSELAGE":
                        self.add_abstract_component(position, Fuselage())
                    if "WING" in node_element:
                        self.add_abstract_component(position, Wing())
                    if "ROTOR" in node_element:
                        self.add_abstract_component(position, Propeller())
                    if "CONNECTOR" in node_element:
                        self.add_abstract_component(position, Connector())

        for position_a, connections in grid.adjacencies.items():
            for position_b in connections:
                self.add_connection(position_a, position_b)


if __name__ == '__main__':
    new_design = AbstractDesign()
    new_design.parse_grid()
