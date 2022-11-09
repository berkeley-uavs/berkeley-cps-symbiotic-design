from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations, product

from igraph import Graph

from sym_cps.representation.design.concrete import DConcrete
from sym_cps.representation.design.concrete.tools import (
    get_subgraph,
    is_isomorphism_present,
    weak_edge_comparison,
    weak_node_comparison,
)
from sym_cps.shared.designs import designs
from sym_cps.tools.graphs import graph_to_pdf


@dataclass
class GraphSet:
    graphs: list[Graph] = field(default_factory=list)

    def add_graph(self, graph):
        if not is_isomorphism_present(self.graphs, graph):
            self.graphs.append(graph)


@dataclass
class Structures:

    graphs: list[Graph] = field(default_factory=list)

    def add_graph(self, graph):
        if not is_isomorphism_present(self.graphs, graph):
            self.graphs.append(graph)

    def add_graphs(self, graphs: list[Graph]):
        for graph in graphs:
            self.add_graph(graph)

    def add_from_designs(self, designs_to_decompose: list[DConcrete], key_nodes: set[str] | None = None):

        if key_nodes is None:
            key_nodes = {"BatteryController", "Tube", "Hub2", "Hub3", "Hub4", "Hub5", "Hub6"}

        subgraphs = []

        for design in designs_to_decompose:
            subgraphs.append(get_subgraph(design, key_nodes).graph.decompose())

        combination_graphs = list(product(*subgraphs))

        same_n_nodes = list(
            filter(lambda x: len(x[1].vs) > 1 and not any(len(x[0].vs) != len(i.vs) for i in x), combination_graphs)
        )

        for graph_set in same_n_nodes:

            isomorphic_graphs = GraphSet()

            pairs = combinations(graph_set, 2)

            for pair in pairs:

                mappings = pair[0].get_isomorphisms_vf2(
                    pair[1], node_compat_fn=weak_node_comparison, edge_compat_fn=weak_edge_comparison
                )
                if len(mappings) > 0:
                    isomorphic_graphs.add_graph(pair[1])

            self.add_graphs(isomorphic_graphs.graphs)


if __name__ == "__main__":
    test_quad = designs["TestQuad"][0]
    new_axe = designs["NewAxe"][0]
    structures = Structures()
    structures.add_from_designs([test_quad, new_axe])
    for i, struct in enumerate(structures.graphs):
        graph_to_pdf(struct, f"structure_{i}", "analysis/structures")
