from __future__ import annotations

import os
from dataclasses import dataclass
from random import choice
from typing import TYPE_CHECKING

import igraph
import pydot
from igraph import Graph, plot
from matplotlib import pyplot as plt
from sym_cps.grammar.tools import get_direction_from_components_and_connections

from sym_cps.representation.library.elements.c_type import CType
from sym_cps.shared.paths import ExportType, designs_folder
from sym_cps.tools.io import save_to_file
from sym_cps.tools.strings import repr_dictionary

if TYPE_CHECKING:
    from sym_cps.representation.design.concrete import DConcrete
    from sym_cps.representation.design.concrete.elements.component import Component


@dataclass
class DTopology:
    name: str

    def __post_init__(self):
        self._graph = Graph()

    @property
    def graph(self) -> Graph:
        return self._graph

    @classmethod
    def from_concrete(cls, d_concrete: DConcrete) -> DTopology:
        # Create all the vertexes with the same id in d_concrete:
        d_topology = cls(name=d_concrete.name)
        for i in range(d_concrete.n_nodes):
            vertex = d_concrete.get_vertex_by_id(i)
            component: Component = vertex["component"]
            d_topology.add_node(c_type=component.library_component.comp_type)
            # print(f"{vertex.index} - {new_vertex.index}")
        for edge in d_concrete.edges:
            d_topology.add_edge(edge.source, edge.target, edge["connection"].direction_b_respect_to_a)
        return d_topology

    @property
    def nodes(self) -> list[igraph.Vertex]:
        return list(self.graph.vs)

    def get_vertex_by_id(self, vid: int) -> igraph.Vertex:
        return self.graph.vs[vid]

    @property
    def edges(self) -> list[igraph.Edge]:
        return list(self.graph.es)

    @property
    def n_nodes(self) -> int:
        return len(self.graph.vs)

    def add_node(self, c_type: CType) -> igraph.Vertex:
        if not isinstance(c_type, CType):
            print(c_type)
            raise Exception("CType wrong")
        return self.graph.add_vertex(c_type=c_type, label=c_type.id)

    def remove_node(self):
        """TODO"""
        raise NotImplementedError

    def add_edge(self, node_id_a: int, node_id_b: int, direction: str = ""):
        self.graph.add_edge(source=node_id_a, target=node_id_b, label=direction)

    def remove_edge(self):
        """TODO. Tip: self.graph.delete_edges"""
        raise NotImplementedError

    @property
    def components(self) -> set[CType]:
        if self.n_nodes > 0:
            return set(self.graph.vs()["c_type"])
        return set()

    def draw_random_node(self) -> igraph.Vertex | None:
        if self.n_nodes == 0:
            return None
        return choice(self.nodes)

    def get_nodes_connected_to(self, node: igraph.Vertex):
        nodes = set()
        for edge in self._graph.es.select(_source=node):
            nodes.add(edge.target)
        return nodes

    @property
    def pydot(self) -> pydot.Dot:
        absolute_folder = designs_folder / self.name
        dot_file_path = absolute_folder / "topology_graph.dot"
        if not dot_file_path.exists():
            self._graph.write_dot(f=str(dot_file_path))
        graphs = pydot.graph_from_dot_file(dot_file_path)
        return graphs[0]

    def export(self, file_type: ExportType):
        absolute_folder = designs_folder / self.name
        if file_type == ExportType.TXT:
            save_to_file(
                str(self),
                file_name=f"DTopology",
                absolute_folder_path=absolute_folder,
            )
        elif file_type == ExportType.JSON:
            raise Exception("Can't create JSON from DTopology. It must be from DConcrete.")
        elif file_type == ExportType.DOT:
            if not os.path.exists(absolute_folder):
                os.makedirs(absolute_folder)
            file_path = absolute_folder / "topology_graph.dot"
            self._graph.write_dot(f=str(file_path))

        elif file_type == ExportType.PDF:
            file_path = absolute_folder / "topology_graph.pdf"
            self.pydot.write_pdf(file_path)

        elif file_type == ExportType.DOT:
            self.graph.write_dot(f=str(absolute_folder / "topo_graph.dot"))

        else:
            raise Exception("File type not supported")

        print(f"{file_type} file saved in {absolute_folder}")

    def export_all(self):
        self.export(ExportType.DOT)
        self.export(ExportType.PDF)
        self.export(ExportType.TXT)

    def __str__(self):
        ret = "TOPOLOGY SUMMARY\n\n"
        connections_map: dict = {}
        for node in self.nodes:
            connections_map[f"{node.index} ({node['c_type']})"] = []
            target_nodes = self.get_nodes_connected_to(node)
            for t_node in target_nodes:
                connections_map[f"{node.index} ({node['c_type']})"].append(self._graph.vs["c_type"][t_node])
        ret += repr_dictionary(connections_map)
        ret += "\n\nGRAPH"
        ret += str(self.graph)
        ret += "\n"
        for node in self.nodes:
            ret += f"{node.index}: {node['c_type']}\n"
        return ret
