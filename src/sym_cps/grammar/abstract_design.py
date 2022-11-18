from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np

import networkx as nx

import matplotlib.pyplot as plt

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
        component.instance_n = c_instance_n
        self.grid[position] = component

    def add_connection(self, position_a: tuple[int, int, int], position_b: tuple[int, int, int]):
        abstract_component_a = self.grid[position_a]
        abstract_component_b = self.grid[position_b]
        abstract_connection = AbstractConnection(abstract_component_a, abstract_component_b)
        self.connections.add(abstract_connection)

    def parse_grid(self, grid: Grid):
        nodes = grid.nodes

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

    @property
    def grid_size(self) -> tuple[int, int, int]:
        max_x = 0
        max_y = 0
        max_z = 0

        for elem in self.grid.keys():
            if elem[0] >= max_x:
                max_x = elem[0]
            if elem[0] >= max_y:
                max_y = elem[0]
            if elem[0] >= max_z:
                max_z = elem[0]

        return max_x, max_y, max_z

    def get_graph(self):

        graph = nx.Graph()

        nodes = {}

        for i, (position, node) in enumerate(self.grid.items()):
            graph.add_node(i,
                           position=np.array(position),
                           id=node.id,
                           color=node.color,
                           component=node)
            nodes[node.id] = i

        for connection in self.connections:
            graph.add_edge(nodes[connection.component_a.id],
                           nodes[connection.component_b.id])

        return graph

    def plot(self):

        graph = self.get_graph()

        # Extract node and edge positions from the layout
        node_xyz = np.array([graph.nodes[v]["position"] for v in sorted(graph)])
        color_xyz = np.array([graph.nodes[v]["color"] for v in sorted(graph)])

        edge_xyz = np.array([(graph.nodes[u]["position"], graph.nodes[v]["position"]) for u, v in graph.edges()])

        # Create the 3D figure
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")

        # Plot the nodes - alpha is scaled by "depth" automatically
        ax.scatter(*node_xyz.T, s=100, ec="w", c=color_xyz)

        # Plot the edges
        for vizedge in edge_xyz:
            ax.plot(*vizedge.T, color="tab:gray")

        # Turn gridlines off
        ax.grid(False)
        # Suppress tick labels
        for dim in (ax.xaxis, ax.yaxis, ax.zaxis):
            dim.set_ticks([1])
        # Set axes labels
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")

        fig.tight_layout()
        plt.show()


if __name__ == '__main__':
    new_design = AbstractDesign()
    new_design.parse_grid(generate_random_topology())
    new_design.plot()


