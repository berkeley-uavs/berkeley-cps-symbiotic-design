from __future__ import annotations

import base64
import hashlib
from dataclasses import dataclass, field

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from sym_cps.grammar import AbstractGrid
from sym_cps.grammar.tools import get_direction_of_tube
from sym_cps.representation.design.abstract.elements import (
    AbstractComponent,
    AbstractConnection,
    Connector,
    Fuselage,
    Propeller,
    Wing,
)
from sym_cps.representation.design.concrete import Component, Connection, DConcrete
from sym_cps.shared.library import c_library
from sym_cps.tools.my_io import save_to_file
from sym_cps.tools.strings import (
    get_component_and_instance_type_from_instance_name,
    get_component_type_from_instance_name,
    get_instance_name,
)


@dataclass
class AbstractDesign:
    name: str
    abstract_grid: AbstractGrid | None = None
    grid: dict[tuple, AbstractComponent] = field(default_factory=dict)
    abstract_connections: set[AbstractConnection] = field(default_factory=set)
    connections: set[Connection] = field(default_factory=set)

    def __hash__(self):
        return hash(self.abstract_grid)

    @property
    def id(self):
        connections_ids = ""
        for connection in self.abstract_connections:
            connections_ids += connection.type_id
            d = hashlib.md5(connections_ids.encode("utf-8")).digest()
            d = base64.urlsafe_b64encode(d).decode("ascii")
            return str(d[:-2])

    def evaluate(self):
        self.save(folder_name=f"designs/{self.name}")

        print(f"Engering")
        d_concrete = self.to_concrete()
        print(f"asdasd")

        d_concrete.choose_default_components_for_empty_ones()
        d_concrete.export_all()
        save_to_file(d_concrete, file_name="d_concrete", folder_name=f"designs/{self.name}")

        print(f"Design {d_concrete.name} generated")
        print(f"Evaluating..")
        d_concrete.evaluate()

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
        self.abstract_connections.add(abstract_connection)

    def parse_grid(self, abstract_grid: AbstractGrid):
        self.abstract_grid = abstract_grid
        self.abstract_grid.name = self.name
        nodes = abstract_grid.nodes
        fuselage_inst = 1
        rotor_inst = 1
        wing_inst = 1
        connecter_inst = 1
        for x_pos, x_axis in enumerate(nodes):
            for y_pos, y_axis in enumerate(x_axis):
                for z_pos, node_element in enumerate(y_axis):
                    position = (x_pos, y_pos, z_pos)
                    if node_element == "FUSELAGE":
                        self.add_abstract_component(
                            position, Fuselage(grid_position=position, instance_n=connecter_inst)
                        )
                        connecter_inst += 1
                    if "WING" in node_element:
                        self.add_abstract_component(position, Wing(grid_position=position, instance_n=wing_inst))
                        wing_inst += 1
                    if "ROTOR" in node_element:
                        self.add_abstract_component(position, Propeller(grid_position=position, instance_n=rotor_inst))
                        rotor_inst += 1
                    if "CONNECTOR" in node_element:
                        self.add_abstract_component(
                            position, Connector(grid_position=position, instance_n=connecter_inst)
                        )
                        connecter_inst += 1

        for position_a, connections in abstract_grid.adjacencies.items():
            for position_b in connections:
                self.add_connection(position_a, position_b)

    def instantiate_hubs(self) -> dict:
        hubs = []
        for component in self.grid.values():
            if component.base_name == "Connector":
                new_hub = {"Hub4_instance_" + str(component.instance_n): {"CONNECTIONS": {}, "PARAMETERS": {}}}
                hubs.append(new_hub)
        return hubs

    def to_concrete(self) -> DConcrete:
        """TODO"""
        d_concrete = DConcrete(name=self.name)
        #
        # tube_id = 1
        # tube_library = c_library.get_default_component("Tube")

        """Connect Tubes to Hubs and Flanges"""
        for abstract_connection in self.abstract_connections:
            concrete_connection_a, concrete_connection_b = abstract_connection.to_concrete_connection()

            d_concrete.connect(concrete_connection_a)
            d_concrete.connect(concrete_connection_b)

        """Connect Structures to themselves"""
        battery_controller = False
        battery_controller_component = None
        for abstract_component in self.grid.values():
            if abstract_component.base_name == "Fuselage_str" or abstract_component.base_name == "Propeller_str_top":
                if not battery_controller:
                    battery_controller_component = Component(
                        c_type=c_library.component_types["BatteryController"],
                        id=get_instance_name("BatteryController", 1),
                        library_component=c_library.get_default_component("BatteryController"),
                    )
                    d_concrete.add_node(battery_controller_component)
                    battery_controller = True

                for comp in abstract_component.structure:
                    if comp.c_type.id == "Motor":
                        new_connection = Connection.from_direction(
                            component_a=battery_controller_component, component_b=comp, direction="ANY"
                        )
                        vertex = d_concrete.get_node_by_instance(comp.c_type.id)
                        if vertex is None:
                            d_concrete.add_node(comp)
                        d_concrete.connect(new_connection)
                    elif comp.c_type.id == "Battery":
                        """First Battery"""
                        new_connection = Connection.from_direction(
                            component_a=battery_controller_component, component_b=comp, direction="ANY"
                        )
                        vertex = d_concrete.get_node_by_instance(comp.c_type.id)
                        if vertex is None:
                            d_concrete.add_node(comp)
                        d_concrete.connect(new_connection)

                        """Second Battery"""
                        instance = int(get_component_and_instance_type_from_instance_name(comp.id)[1]) + 1
                        battery_component_2 = Component(
                            c_type=c_library.component_types["Battery"],
                            id=get_instance_name("Battery", instance),
                            library_component=c_library.get_default_component("Battery"),
                        )
                        new_connection = Connection.from_direction(
                            component_a=battery_controller_component, component_b=battery_component_2, direction="ANY"
                        )
                        vertex = d_concrete.get_node_by_instance(battery_component_2.c_type.id)
                        if vertex is None:
                            d_concrete.add_node(battery_component_2)
                        d_concrete.connect(new_connection)

                for connections in abstract_component.connections:
                    component_a = connections.component_a
                    component_b = connections.component_b

                    vertex_a = d_concrete.get_node_by_instance(component_a.c_type.id)
                    if vertex_a is None:
                        d_concrete.add_node(component_a)

                    vertex_b = d_concrete.get_node_by_instance(component_b.id)
                    if vertex_b is None:
                        d_concrete.add_node(component_b)

                    self.connections.add(connections)
                    # print(f"Connecting {connections.component_a.id} to {connections.component_b.id}")
                    d_concrete.connect(connections)

        return d_concrete

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

        for connection in self.abstract_connections:
            graph.add_edge(nodes[connection.component_a.id], nodes[connection.component_b.id])

        return graph

    def save(self, folder_name: str | None = None):
        export: dict = {"NODES": {}, "EDGES": []}
        for position, component in self.grid.items():
            export["NODES"][component.id] = position
        for connection in self.abstract_connections:
            export["EDGES"].append((connection.component_a.id, connection.component_b.id))

        if folder_name is None:
            folder_name = "grammar"

        save_to_file(export, file_name="grid", folder_name=folder_name)
        save_to_file(self.abstract_grid, file_name="grid", folder_name=folder_name)
        save_to_file(self.plot, file_name="grid", folder_name=folder_name)

    @property
    def plot(self):

        graph = self.graph
        list_xyz = [graph.nodes[v]["position"] for v in sorted(graph)]
        print(list_xyz)
        # Extract node and edge positions from the layout
        node_xyz = np.array([graph.nodes[v]["position"] for v in sorted(graph)])
        print(node_xyz)
        color_xyz = np.array([graph.nodes[v]["color"] for v in sorted(graph)])
        print(color_xyz)

        edge_xyz = np.array([(graph.nodes[u]["position"], graph.nodes[v]["position"]) for u, v in graph.edges()])
        print(edge_xyz)

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
