from __future__ import annotations

from dataclasses import dataclass, field

from sym_cps.grammar.elements import AbstractComponent, AbstractConnection, Fuselage, Wing, Propeller, Connector
from sym_cps.grammar.rules import generate_random_topology, Grid


@dataclass
class AbstractDesign:
    grid: dict[tuple, AbstractComponent] = field(default_factory=dict)
    connections: set[AbstractConnection] = field(default_factory=set)

    def add_abstract_component(self,
                               position: tuple[int, int, int],
                               component: AbstractComponent):
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
