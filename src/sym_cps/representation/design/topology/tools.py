from __future__ import annotations

from igraph import Graph, Vertex
from sym_cps.representation.design.topology import DTopology
from sym_cps.shared.designs import designs


def node_comparison(graph_1: Graph, graph_2: Graph, node_1: Vertex, node_2: Vertex):
    c1 = graph_1.vs[node_1]["c_type"]
    c2 = graph_2.vs[node_2]["c_type"]
    equal = c1 == c2
    return equal


def edge_comparison(graph_1: Graph, graph_2: Graph, edge_1: int, edge_2: int):
    c1 = graph_1.es[edge_1]["connection"]
    c2 = graph_2.es[edge_2]["connection"]
    return c1 == c2


def get_subisomorphisms(design_1: DTopology, design_2: DTopology):
    mappings = design_1.graph.get_subisomorphisms_vf2(
        design_2.graph, node_compat_fn=node_comparison, edge_compat_fn=edge_comparison
    )

    print(mappings)



if __name__ == '__main__':
    design_1 = designs["NewAxe_Cargo"][1]
    design_2 = designs["TestQuad_Cargo"][1]
    get_subisomorphisms(design_1, design_2)