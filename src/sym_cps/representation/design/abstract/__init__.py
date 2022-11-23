from __future__ import annotations

from dataclasses import dataclass, field

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from sym_cps.representation.design.abstract.elements import AbstractComponent, AbstractConnection, Connector, Fuselage, Propeller, Wing
from sym_cps.grammar.rules import Grid, generate_random_topology, get_seed_design_topo
from sym_cps.tools.my_io import save_to_file


@dataclass
class AbstractDesign:
    name: str
    grid: dict[tuple, AbstractComponent] = field(default_factory=dict)
    connections: set[AbstractConnection] = field(default_factory=set)

    def add_abstract_component(self, position: tuple[int, int, int], component: AbstractComponent):
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

    def instantiate_hubs(self) -> dict:
        hubs = []
        for component in self.grid.values():
            if component.base_name == "Connector":
                new_hub = {"Hub6_instance_" + str(component.instance_n): {"CONNECTIONS": {}, "PARAMETERS": {}}}
                hubs.append(new_hub)
        return hubs

    def instantiate_tubes(self, num_hubs) -> dict:
        """TODO"""
        """
        "Tube_instance_1": {
            "CONNECTIONS": {
                "Fuselage_str_instance_1__Hub4": "SIDE4-BOTTOM",
                "Propeller_str_top_instance_2__Flange": "TOP-SIDE"
            },
            "PARAMETERS": {
                "Tube__END_ROT": 0.0,
                "Tube__Length": 400.0,
                "Tube__Offset1": 0.0
            }
        },
        "Tube_instance_2": {
            "CONNECTIONS": {
                "Fuselage_str_instance_1__Hub4": "SIDE1-BOTTOM",
                "Propeller_str_top_instance_3__Flange": "TOP-SIDE"
            },
            "PARAMETERS": {
                "Tube__END_ROT": 0.0,
                "Tube__Length": 400.0,
                "Tube__Offset1": 0.0
            }
        },
        """
        hub_counter = [1 for _ in range(num_hubs)]
        fuselage_counter = {}
        tubes = []
        instance = 1
        for connection in self.connections:
            # if connection.component_a.base_name == "Propeller_str":
            #     current = connection.component_a
            #     other = connection.component_b
            #     new_tube = self.get_tube_for_propeller(current, other, length, instance, hub_counter)
            # elif connection.component_a.base_name == "Fuselage_str":
            #     other = connection.component_b
            #     current = connection.component_a
            #     new_tube = self.get_tube_for_fuselage(current, other, length, instance, hub_counter)
            # elif connection.component_a.base_name == "Wing":
            #     current = connection.component_a
            #     other = connection.component_b
            #     new_tube = self.get_tube_for_wing(current, other, length, instance, hub_counter)
            # elif connection.component_a.base_name == "Connector":
            #     current = connection.component_a
            #     other = connection.component_b
            #     new_tube = self.get_tube_for_hubs(current, other, length, instance, hub_counter)
            #     hub_counter[connection.component_a.instance_n - 1] += 1
            if connection.component_a.base_name == "Fuselage_str":
                if not connection.component_a.instance_n in fuselage_counter.keys():
                    fuselage_counter[connection.component_a.instance_n] = 1
                else:
                    fuselage_counter[connection.component_a.instance_n] += 1
            if connection.component_b.base_name == "Fuselage_str":
                if not connection.component_b.instance_n in fuselage_counter.keys():
                    fuselage_counter[connection.component_b.instance_n] = 1
                else:
                    fuselage_counter[connection.component_b.instance_n] += 1

            length = 400 * connection.euclid_distance
            new_tube = self.get_tube(
                connection.component_a, connection.component_b, length, instance, hub_counter, fuselage_counter
            )

            if connection.component_a.base_name == "Connector":
                hub_counter[connection.component_a.instance_n - 1] += 1
            if connection.component_b.base_name == "Connector":
                hub_counter[connection.component_b.instance_n - 1] += 1

            tubes.append(new_tube)
            instance += 1
            # Connect it based on connection.relative_position
        return tubes

    def get_mapping(self, component):
        mapping = {
            "Propeller_str": component.base_name + "_top_instance_" + str(component.instance_n),
            "Fuselage_str": component.id,
            "Wing": component.id,
            "Connector": "Hub6_instance_" + str(component.instance_n),
        }
        return mapping[component.base_name]

    def get_tube(self, current, other, length, instance, hub_counter, fuselage_counter):
        comp_a = self.get_mapping(current)
        comp_b = self.get_mapping(other)
        tube_instance = "Tube_instance_" + str(instance)

        new_tube = {
            tube_instance: {
                "CONNECTIONS": {},
                "PARAMETERS": {"Tube__END_ROT": 0.0, "Tube__Length": length, "Tube__Offset1": 0.0},
            }
        }

        if current.base_name == "Fuselage_str":
            side = fuselage_counter[current.instance_n]
            new_tube[tube_instance]["CONNECTIONS"][comp_a + "__Hub4"] = "SIDE" + str(side) + "-BOTTOM"
        elif current.base_name == "Wing":
            new_tube[tube_instance]["CONNECTIONS"][comp_a] = "BOTTOM"
        elif current.base_name == "Propeller_str":
            new_tube[tube_instance]["CONNECTIONS"][comp_a + "__Flange"] = "TOP-SIDE"
        elif current.base_name == "Connector":
            new_tube[tube_instance]["CONNECTIONS"][comp_a] = (
                "SIDE" + str(hub_counter[current.instance_n - 1]) + "-BOTTOM"
            )

        if other.base_name == "Fuselage_str":
            side = fuselage_counter[other.instance_n]
            new_tube[tube_instance]["CONNECTIONS"][comp_b + "__Hub4"] = "SIDE" + str(side) + "-BOTTOM"
        elif other.base_name == "Wing":
            new_tube[tube_instance]["CONNECTIONS"][comp_b] = "BOTTOM"
        elif other.base_name == "Propeller_str":
            new_tube[tube_instance]["CONNECTIONS"][comp_b + "__Flange"] = "TOP-SIDE"
        elif other.base_name == "Connector":
            new_tube[tube_instance]["CONNECTIONS"][comp_b] = "SIDE" + str(hub_counter[other.instance_n - 1]) + "-BOTTOM"

        return new_tube

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

    @property
    def graph(self):

        graph = nx.Graph()

        nodes = {}

        for i, (position, node) in enumerate(self.grid.items()):
            graph.add_node(i, position=np.array(position), id=node.id, color=node.color, component=node)
            nodes[node.id] = i

        for connection in self.connections:
            graph.add_edge(nodes[connection.component_a.id], nodes[connection.component_b.id])

        return graph

    def save(self, folder_name: str | None = None):
        export: dict = {"NODES": {}, "EDGES": []}
        for position, component in self.grid.items():
            export["NODES"][component.id] = position
        for connection in self.connections:
            export["EDGES"].append((connection.component_a.id, connection.component_b.id))

        if folder_name is None:
            folder_name = "grammar"

        save_to_file(export, file_name=self.name, folder_name=folder_name)
        save_to_file(self.plot, file_name=self.name, folder_name=folder_name)
        save_to_file(self, file_name=self.name, folder_name=folder_name)

    @property
    def plot(self):

        graph = self.graph

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
            dim.set_ticks([])
        # Set axes labels
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")

        fig.tight_layout()
        # fig.show()
        return fig


if __name__ == "__main__":
    # new_design.parse_grid(get_seed_design_topo("TestQuad_Cargo"))

    new_design = AbstractDesign(f"TestQuad_Cargo")
    # new_design.parse_grid(generate_random_topology())
    new_design.parse_grid(get_seed_design_topo("TestQuad_Cargo"))
    new_design.save()

    for i in range(0, 100):
        new_design = AbstractDesign(f"random_{i}")
        new_design.parse_grid(generate_random_topology())
        new_design.save()
