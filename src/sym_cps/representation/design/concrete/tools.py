from __future__ import annotations

import hashlib
from copy import deepcopy
from itertools import combinations, product

from igraph import Edge, Graph, Vertex

from sym_cps.representation.design.concrete import DConcrete
from sym_cps.shared.objects import ExportType


def is_isomorphism_present(graphs: list[Graph], graph_to_add: Graph):
    for g in graphs:
        if (
            len(
                g.get_isomorphisms_vf2(
                    graph_to_add, node_compat_fn=weak_node_comparison, edge_compat_fn=weak_edge_comparison
                )
            )
            > 0
        ):
            return True
    return False


def find_isomorphisms(elements: list[Graph]) -> tuple[list[Graph], bool]:
    isomorphisms = []
    all_elements_are_isomorphic = True
    pairs = combinations(elements, 2)
    for pair in pairs:
        mappings = pair[0].get_isomorphisms_vf2(
            pair[1], node_compat_fn=weak_node_comparison, edge_compat_fn=weak_edge_comparison
        )
        if len(mappings) > 0:
            if not is_isomorphism_present(isomorphisms, pair[0]):
                isomorphisms.append(pair[0])
        else:
            all_elements_are_isomorphic = False
    return isomorphisms, all_elements_are_isomorphic


def node_comparison(graph_1: Graph, graph_2: Graph, node_1: Vertex, node_2: Vertex):
    c1 = graph_1.vs[node_1]["component"]
    c2 = graph_2.vs[node_2]["component"]
    equal = c1 == c2
    return equal


def edge_comparison(graph_1: Graph, graph_2: Graph, edge_1: int, edge_2: int):
    c1 = graph_1.es[edge_1]["connection"]
    c2 = graph_2.es[edge_2]["connection"]
    return c1 == c2


def get_edges_connected_to_types(design: DConcrete, types_to_check: set[str]) -> set[Edge]:
    nodes_to_check = set()
    for comp_type in types_to_check:
        nodes_to_check |= set(design.graph.vs.select(label=comp_type))
    edges_to_remove = set()
    for node in nodes_to_check:
        edges_to_remove |= design.get_edges_connected_to(node.index)
    return edges_to_remove


cheap_hash = lambda input: hashlib.md5(input).hexdigest()[:6]
hash = hashlib.sha1("my message".encode("UTF-8")).hexdigest()


def get_subgraph(design: DConcrete, key_nodes: list[str]) -> DConcrete:
    design_ret = deepcopy(design)
    edges_to_remove = get_edges_connected_to_types(design, key_nodes)
    design_ret.graph.delete_edges(edges_to_remove)
    key_nodes_str = "-".join(key_nodes)
    design_ret.export(
        ExportType.PDF, folder=f"analysis/isomorphisms/{key_nodes_str}/decompositions", tag=f"_decomposed_{design.name}"
    )
    return design_ret


def weak_node_comparison(graph_1: Graph, graph_2: Graph, node_1: Vertex, node_2: Vertex):
    c1 = graph_1.vs[node_1]["c_type"].id
    c2 = graph_2.vs[node_2]["c_type"].id
    return c1 == c2


def weak_edge_comparison(graph_1: Graph, graph_2: Graph, edge_1: int, edge_2: int):
    c1 = graph_1.es[edge_1]["label"]
    c2 = graph_2.es[edge_2]["label"]
    return c1 == c2


def get_subgraphs_isomorphisms(designs_to_decompose: list[DConcrete], key_nodes: set[str]):
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
        mappings = graph_1.get_isomorphisms_vf2(
            graph_2, node_compat_fn=weak_node_comparison, edge_compat_fn=weak_edge_comparison
        )
        for map in mappings:
            structure = []
            for node in map:
                structure.append(graph_2.vs(node))

    print(mappings)
