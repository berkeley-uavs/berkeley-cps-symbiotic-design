from __future__ import annotations

import hashlib
from copy import deepcopy
from itertools import combinations, product

from igraph import Edge, Graph, Vertex

from sym_cps.representation.design.concrete import DConcrete
from sym_cps.tools.graphs import graph_to_dict


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


# def same_instanciation(struct_a: dict, struct_b: dict):
#     print(struct_a)
#     print(struct_b)
#
#     return True

def strong_mapping(graph_a: Graph, graph_b: Graph) -> bool:
    mappings = graph_a.get_isomorphisms_vf2(
        graph_b, node_compat_fn=node_comparison, edge_compat_fn=edge_comparison
    )
    return len(mappings) > 0


# def strong_mapping_dict(gra)
def find_isomorphisms(elements: list[Graph]) -> tuple[dict[str, list[dict]], dict[str, Graph], bool]:
    set_of_types_a = set([vs["label"] for vs in elements[0].vs])
    for e in elements[1:]:
        set_of_types_b = set([vs["label"] for vs in e.vs])
        if set_of_types_a != set_of_types_b:
            print("Uncomparable")
            return {}, {}, {}

    isomorphisms_summary = {}
    isomorphisms_graphs_summary = {}
    iso_graphs = {}
    all_elements_with_same_nodes_types_are_isomorphic = True
    pairs = combinations(elements, 2)
    for pair in pairs:
        mappings = pair[0].get_isomorphisms_vf2(
            pair[1], node_compat_fn=weak_node_comparison, edge_compat_fn=weak_edge_comparison
        )
        if len(mappings) > 0:
            iso_a_key, iso_a_struct = graph_to_dict(pair[0])
            iso_b_key, iso_b_struct = graph_to_dict(pair[1])
            iso_graphs[iso_a_key] = pair[0]
            if iso_a_key not in isomorphisms_summary.keys():
                isomorphisms_summary[iso_a_key] = [iso_a_struct]
                isomorphisms_graphs_summary[iso_a_key] = [pair[0]]
            append_a = True
            append_b = True
            for elem in isomorphisms_graphs_summary[iso_a_key]:
                if strong_mapping(pair[0], elem):
                    append_a = False
                if strong_mapping(pair[1], elem):
                    append_b = False
            if append_a:
                isomorphisms_summary[iso_a_key].append(iso_a_struct)
                isomorphisms_graphs_summary[iso_a_key].append(pair[0])
            if append_b:
                isomorphisms_summary[iso_b_key].append(iso_b_struct)
                isomorphisms_graphs_summary[iso_a_key].append(pair[1])

        else:
            all_elements_with_same_nodes_types_are_isomorphic = False
            # set_of_types_a = set([vs["label"] for vs in pair[0].vs])
            # set_of_types_b = set([vs["label"] for vs in pair[1].vs])
            # if set_of_types_a != set_of_types_b:
            #     all_elements_with_same_nodes_types_are_isomorphic = False
    return isomorphisms_summary, iso_graphs, all_elements_with_same_nodes_types_are_isomorphic


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

all_types = {
    "SensorRpmTemp",
    "SensorVariometer",
    "Cargo",
    "Propeller",
    "BatteryController",
    "SensorCurrent",
    "SensorAutopilot",
    "Hub4",
    "Orient",
    "Hub3",
    "Battery",
    "Wing",
    "Hub2",
    "CargoCase",
    "Motor",
    "Flange",
    "SensorGPS",
    "Fuselage",
    "SensorVoltage",
    "Tube",
}
sensors = set()
hubs = set()

for t in all_types:
    if "Sensor" in t:
        sensors.add(t)
    if "Hub" in t:
        hubs.add(t)


def get_subgraph(design: DConcrete, key_nodes: list[str]) -> DConcrete:
    design_ret = deepcopy(design)

    if "Sensor" in key_nodes:
        key_nodes.remove("Sensor")
        key_nodes.extend(list(sensors))
    if "Hub" in key_nodes:
        key_nodes.remove("Hub")
        key_nodes.extend(list(hubs))
    edges_to_remove = get_edges_connected_to_types(design, key_nodes)
    design_ret.graph.delete_edges(edges_to_remove)
    # key_nodes_str = "-".join(key_nodes)
    # design_ret.export(
    #     ExportType.PDF, folder=f"analysis/isomorphisms/{key_nodes_str}/decompositions", tag=f"_decomposed_{design.name}"
    # )
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
