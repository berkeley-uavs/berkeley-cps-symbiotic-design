from __future__ import annotations
from dataclasses import dataclass, field


from random import choice
from typing import TYPE_CHECKING

import igraph
from igraph import Graph
from sym_cps.representation.library.elements.c_type import CType
from sym_cps.shared.paths import ExportType, designs_folder
from sym_cps.tools.io import save_to_file

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
            d_topology.add_edge(edge.source, edge.target)
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
        return self.graph.add_vertex(c_type=c_type, label=c_type.id)

    def remove_node(self):
        """TODO"""
        raise NotImplementedError

    def add_edge(self, node_id_a: int, node_id_b: int):
        self.graph.add_edge(source=node_id_a, target=node_id_b)

    def remove_edge(self):
        """TODO. Tip: self.graph.delete_edges"""
        raise NotImplementedError

    @property
    def components(self) -> set[CType]:
        if self.n_nodes > 0:
            return set(self.graph.vs()["c_type"])
        return set()

    @property
    def edges(self) -> list[igraph.Edge]:
        return list(self.graph.es)

    def draw_random_node(self) -> igraph.Vertex | None:
        if self.n_nodes == 0:
            return None
        return choice(self.nodes)


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
            self.graph.write_dot(f=str(absolute_folder / "topo_graph.dot"))

        else:
            raise Exception("File type not supported")

        print(f"{file_type} file saved in {absolute_folder}")



    def __str__(self):
        ret = str(self.graph)
        ret += "\n"
        for node in self.nodes:
            ret += f"{node.index}: {node['c_type']}\n"
        return ret
