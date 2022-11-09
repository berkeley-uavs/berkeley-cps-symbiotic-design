from __future__ import annotations

from copy import deepcopy
from itertools import product

from igraph import Edge, Graph, Vertex

from sym_cps.representation.design.topology import DTopology
from sym_cps.shared.designs import designs
from sym_cps.shared.objects import ExportType

cut_nodes_1 = {"BatteryController", "Hub2", "Hub3", "Hub4", "Hub5", "Hub6"}
key_nodes_2 = {"BatteryController", "Tube", "Hub2", "Hub3", "Hub4", "Hub5", "Hub6"}


def get_edges_connected_to_types(design: DTopology, types_to_check: set[str]) -> set[Edge]:
    nodes_to_check = set()
    for comp_type in types_to_check:
        nodes_to_check |= set(design.graph.vs.select(label=comp_type))
    edges_to_remove = set()
    for node in nodes_to_check:
        edges_to_remove |= design.get_edges_connected_to(node.index)
    return edges_to_remove


def get_subgraph(design: DTopology, key_nodes: set[str]) -> DTopology:
    design_ret = deepcopy(design)
    edges_to_remove = get_edges_connected_to_types(design, key_nodes)
    design_ret.graph.delete_edges(edges_to_remove)
    design_ret.export(ExportType.PDF, tag="_subgraph_1")
    return design_ret


def node_comparison(graph_1: Graph, graph_2: Graph, node_1: Vertex, node_2: Vertex):
    c1 = graph_1.vs[node_1]["label"]
    c2 = graph_2.vs[node_2]["label"]
    return c1 == c2


def edge_comparison(graph_1: Graph, graph_2: Graph, edge_1: int, edge_2: int):
    c1 = graph_1.es[edge_1]["label"]
    c2 = graph_2.es[edge_2]["label"]
    return c1 == c2


def get_subgraphs_isomorphisms(designs_to_decompose: list[DTopology], key_nodes: set[str]):

    subgraphs = []

    for design in designs_to_decompose:
        subgraphs.append(get_subgraph(design, key_nodes).graph.decompose())

    mappings = []
    combination_graphs = list(product(*subgraphs))
    same_n_nodes = list(filter(lambda x: len(x[0].vs) == len(x[1].vs) and len(x[1].vs) > 1, combination_graphs))
    for pair in same_n_nodes:
        graph_1 = pair[0]
        graph_2 = pair[1]
        print(graph_1)
        print(graph_2)
        mappings = graph_1.get_isomorphisms_vf2(graph_2, node_compat_fn=node_comparison, edge_compat_fn=edge_comparison)
        for map in mappings:
            structure = []
            for node in map:
                structure.append(graph_2.vs(node))

    print(mappings)


if __name__ == "__main__":
    test_quad = designs["TestQuad"][1]
    new_axe = designs["NewAxe"][1]
    get_subgraphs_isomorphisms([test_quad, new_axe], key_nodes=key_nodes_2)
