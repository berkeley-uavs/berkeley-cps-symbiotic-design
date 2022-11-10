from __future__ import annotations

import json
import os
import random
from itertools import product

from sym_cps.representation.design.concrete import DConcrete
from sym_cps.representation.design.concrete.tools import find_isomorphisms, get_subgraph, is_isomorphism_present
from sym_cps.shared.designs import designs
from sym_cps.shared.paths import output_folder
from sym_cps.tools.graphs import graph_to_dict, graph_to_pdf
from sym_cps.tools.my_io import save_to_file


def find_isos(designs_to_decompose: list[DConcrete], key_nodes: list[str] | None = None):
    if key_nodes is None:
        key_nodes = ["BatteryController", "Tube", "Hub2", "Hub3", "Hub4", "Hub5", "Hub6"]

    subgraphs = []

    for design in designs_to_decompose:

        dec_designs: dict[int, list] = {}
        decompositions = get_subgraph(design, key_nodes).graph.decompose()
        for dec in decompositions:
            size = len(dec.vs)
            if size > 1:
                if size in dec_designs.keys():
                    if not is_isomorphism_present(list(dec_designs[size]), dec):
                        dec_designs[size].append(dec)
                else:
                    dec_designs[size] = [dec]
        if len(dec_designs.keys()) > 0:
            subgraphs.append(dec_designs)

    if len(subgraphs) <= 1:
        return [], []

    n_nodes_min = 100
    n_nodes_max = 1
    for elem in subgraphs:
        loc_min = min(elem.keys())
        loc_max = max(elem.keys())
        if loc_min <= n_nodes_min:
            n_nodes_min = loc_min
        if loc_max >= n_nodes_max:
            n_nodes_max = loc_max

    candiates = {}

    key_nodes_str = "-".join(key_nodes)
    export_folder = f"analysis/isomorphisms/{key_nodes_str}/candidates/"
    if not os.path.exists(export_folder):
        os.makedirs(export_folder)

    for i in range(n_nodes_min, n_nodes_max + 1):
        proposals = []
        for elem in subgraphs:
            if i in elem.keys():
                proposals.append(elem[i])
        if len(proposals) > 0:
            candiates[i] = list(product(*proposals))

    local_iso = []
    global_iso = []
    for n_nodes, combinations in candiates.items():
        for combination in combinations:
            isomorphisms, all_elements = find_isomorphisms(combination)
            if all_elements and len(combination) == len(designs_to_decompose):
                global_iso.extend(isomorphisms)
            else:
                local_iso.extend(isomorphisms)

    for n_nodes, candidates in candiates.items():
        for i, groups in enumerate(candidates):
            for j, graph in enumerate(groups):
                graph_to_pdf(graph, f"{n_nodes}_{i}_{j}_graph", export_folder)

    print(f"Found {len(local_iso)} local isomorphisms and {len(global_iso)} global ones")
    return local_iso, global_iso


def explore_structures(designs: list[DConcrete], key_nodes: list[str]):
    local_iso, global_iso = find_isos(designs, key_nodes)

    key_nodes_str = "-".join(key_nodes)
    export_folder = f"analysis/isomorphisms/{key_nodes_str}/structures"

    summary = {"LOCAL": [], "GLOBAL": []}

    for i, iso in enumerate(local_iso):
        structure = graph_to_dict(iso, f"local_{i}")
        summary["LOCAL"].append(structure)
        save_to_file(structure, f"local_{i}.json", folder_name=export_folder)
        graph_to_pdf(iso, f"local_{i}.json", export_folder)

    for i, iso in enumerate(global_iso):
        structure = graph_to_dict(iso, f"global_{i}")
        summary["GLOBAL"].append(structure)
        save_to_file(structure, f"global_{i}.json", folder_name=export_folder)
        graph_to_pdf(iso, f"global_{i}", export_folder)

    save_to_file(summary, f"summary.json", folder_name=f"analysis/isomorphisms/{key_nodes_str}")
    return summary


def predefined_nodes(designs_chosen):
    key_nodes = ["BatteryController", "Tube", "Hub2", "Hub3", "Hub4", "Hub5", "Hub6"]
    return explore_structures(designs_chosen, key_nodes)


def random_sampling(designs_chosen, nodes_types):
    subset = random.sample(nodes_types, random.randint(1, len(nodes_types)))
    print(f"Node keys: {subset}")
    return explore_structures(designs_chosen, subset), subset


def random_sampling_for_n(iterations: int = 10000):
    designs_chosen = [d[0] for d in designs.values()]
    nodes_types = set()
    for d in designs_chosen:
        nodes_types |= d.all_comp_types_ids

    iteration = 0
    total_summary = {}

    while iteration < iterations:
        print(f"Iteration: {iteration}")
        summary, subset = random_sampling(designs_chosen, nodes_types)
        summary_file = output_folder / "analysis/isomorphisms/structure_summary.json"
        exiting_entries = 0
        if summary_file.is_file():
            existing_summary: dict = json.load(open(output_folder / "analysis/isomorphisms/structure_summary.json"))
            exiting_entries = len(existing_summary.keys())
            total_summary = existing_summary
        l_hits = len(summary["LOCAL"])
        g_hits = len(summary["GLOBAL"])
        t_hits = l_hits + g_hits
        total_summary[str(exiting_entries + iteration)] = {
            "HITS": t_hits,
            "LOCAL": l_hits,
            "GLOBAL": g_hits,
            "KEYS": list(subset),
        }

        save_to_file(total_summary, "structure_summary.json", f"analysis/isomorphisms/")
        iteration += 1


if __name__ == "__main__":
    designs_chosen = [d[0] for d in designs.values()]
    # predefined_nodes(designs_chosen)
    random_sampling_for_n(4)
