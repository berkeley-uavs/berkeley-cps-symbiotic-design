from __future__ import annotations

import json
import os
import random
from itertools import product

from sym_cps.representation.design.concrete import DConcrete
from sym_cps.representation.design.concrete.tools import find_isomorphisms, get_subgraph, is_isomorphism_present
from sym_cps.shared.designs import designs
from sym_cps.shared.paths import output_folder, popular_nodes_keys_path
from sym_cps.tools.graphs import graph_to_dict, graph_to_pdf
from sym_cps.tools.my_io import save_to_file
from sym_cps.tools.strings import make_hash_sha256


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
                for iso in isomorphisms:
                    if not is_isomorphism_present(global_iso, iso):
                        global_iso.append(iso)
            else:
                for iso in isomorphisms:
                    if not is_isomorphism_present(local_iso, iso):
                        local_iso.append(iso)

    # for n_nodes, candidates in candiates.items():
    #     for i, groups in enumerate(candidates):
    #         for j, graph in enumerate(groups):
    #             graph_to_pdf(graph, f"{n_nodes}_{i}_{j}_graph", export_folder)

    print(f"Found {len(local_iso)} local isomorphisms and {len(global_iso)} global ones")
    return local_iso, global_iso


def explore_structures(designs: list[DConcrete], key_nodes: list[str]):
    local_iso, global_iso = find_isos(designs, key_nodes)

    key_nodes_str = "-".join(key_nodes)

    summary = {"LOCAL": {}, "GLOBAL": {}}

    graphs_dict = {}

    for i, iso in enumerate(local_iso):
        structure_key, structure = graph_to_dict(iso)
        graphs_dict[structure_key] = iso
        structure_hash = str(make_hash_sha256(structure))[-5:]
        if structure_key not in summary["LOCAL"]:
            structure["COUNT"] = 1
            summary["LOCAL"] = {structure_key: {"VARIANTS": {structure_hash: structure}}}
        else:
            if structure_hash not in summary["LOCAL"][structure_key]["VARIANTS"].keys():
                structure["COUNT"] = 1
                summary["LOCAL"][structure_key]["VARIANTS"][structure_hash] = structure
            else:
                summary["LOCAL"][structure_key]["VARIANTS"][structure_hash]["COUNT"] += 1

    for i, iso in enumerate(global_iso):
        structure_key, structure = graph_to_dict(iso)
        graphs_dict[structure_key] = iso
        structure_hash = str(make_hash_sha256(structure))[-5:]
        if structure_key not in summary["GLOBAL"]:
            structure["COUNT"] = 1
            summary["GLOBAL"] = {structure_key: {"VARIANTS": {structure_hash: structure}}}
        else:
            if structure_hash not in summary["GLOBAL"][structure_key]["VARIANTS"].keys():
                structure["COUNT"] = 1
                summary["GLOBAL"][structure_key]["VARIANTS"][structure_hash] = structure
            else:
                summary["GLOBAL"][structure_key]["VARIANTS"][structure_hash]["COUNT"] += 1

    # save_to_file(summary, f"summary.json", folder_name=f"analysis/isomorphisms/{key_nodes_str}")
    return summary, graphs_dict


def predefined_nodes(designs_chosen):
    key_nodes = ["BatteryController", "Tube", "Hub2", "Hub3", "Hub4", "Hub5", "Hub6"]
    return explore_structures(designs_chosen, key_nodes)


def random_sampling(designs_chosen, nodes_types):
    subset = random.sample(nodes_types, random.randint(1, len(nodes_types)))
    print(f"Node keys: {subset}")
    subset = ["BatteryController", "Tube", "Hub2", "Hub3", "Hub4", "Hub5", "Hub6"]
    return explore_structures(designs_chosen, subset)


popular_nodes: dict = json.load(open(popular_nodes_keys_path))
popular_nodes_list: list = list(popular_nodes.keys())


def random_sampling_for_n(iterations: int = 10000):
    designs_chosen = [d[0] for d in designs.values()]
    nodes_types = set()
    for d in designs_chosen:
        nodes_types |= d.all_comp_types_ids
    node_types_default = {
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

    node_types_grouped = set()

    for node in node_types_default:
        if "Sensor" in node:
            node_types_grouped.add("Sensor")
        elif "Hub" in node:
            node_types_grouped.add("Hub")
        else:
            node_types_grouped.add(node)

    summary_file = output_folder / "analysis/isomorphisms/structure_summary.json"
    if summary_file.is_file():
        total_summary: dict = json.load(open(output_folder / "analysis/isomorphisms/structure_summary.json"))
    else:
        total_summary = {"LOCAL": {}, "GLOBAL": {}}

    graphs_dict_total = {}

    iteration = 1
    nodes_types_set_visited = []
    while iteration < iterations:
        print(f"Iteration: {iteration}")
        if iteration < 1:
            nodes_types_set = popular_nodes_list[iteration].split("-")
            print("Choosing popular node types:")
        else:
            print("Choosing randomly:")
            nodes_types_set = random.sample(node_types_grouped, random.randint(1, len(node_types_grouped)))
        print(nodes_types_set)
        nodes_types_set_list = sorted(list(nodes_types_set))
        nodes_types_str = "-".join(nodes_types_set_list)
        if nodes_types_set_list in nodes_types_set_visited:
            continue
        summary, graphs_dict = explore_structures(designs_chosen, nodes_types_set)
        graphs_dict_total.update(graphs_dict)

        for structure_key, structure in summary["LOCAL"].items():
            if structure_key not in total_summary["LOCAL"].keys():
                total_summary["LOCAL"][structure_key] = summary["LOCAL"][structure_key]
                total_summary["LOCAL"][structure_key]["KEYS"] = [nodes_types_str]
                total_summary["LOCAL"][structure_key]["COUNT"] = 1
            else:
                for struct_hash, struct in summary["LOCAL"][structure_key]["VARIANTS"].items():
                    if struct_hash not in summary["LOCAL"][structure_key]["VARIANTS"].keys():
                        summary["LOCAL"][structure_key]["VARIANTS"][struct_hash] = summary["LOCAL"][structure_key][
                            "VARIANTS"
                        ][struct_hash]
                    else:
                        summary["LOCAL"][structure_key]["VARIANTS"][struct_hash]["COUNT"] += 1
                if nodes_types_str not in total_summary["LOCAL"][structure_key]["KEYS"]:
                    total_summary["LOCAL"][structure_key]["KEYS"].append(nodes_types_str)
                total_summary["LOCAL"][structure_key]["COUNT"] += 1
        for structure_key, structure in summary["GLOBAL"].items():
            if structure_key not in total_summary["GLOBAL"].keys():
                total_summary["GLOBAL"][structure_key] = summary["GLOBAL"][structure_key]
                total_summary["GLOBAL"][structure_key]["KEYS"] = [nodes_types_str]
                total_summary["GLOBAL"][structure_key]["COUNT"] = 1
            else:
                for struct_hash, struct in summary["GLOBAL"][structure_key]["VARIANTS"].items():
                    if struct_hash not in summary["GLOBAL"][structure_key]["VARIANTS"].keys():
                        summary["GLOBAL"][structure_key]["VARIANTS"][struct_hash] = summary["GLOBAL"][structure_key][
                            "VARIANTS"
                        ][struct_hash]
                    else:
                        summary["GLOBAL"][structure_key]["VARIANTS"][struct_hash]["COUNT"] += 1
                if nodes_types_str not in total_summary["GLOBAL"][structure_key]["KEYS"]:
                    total_summary["GLOBAL"][structure_key]["KEYS"].append(nodes_types_str)
                total_summary["GLOBAL"][structure_key]["COUNT"] += 1

        save_to_file(total_summary, "structure_summary.json", f"analysis/isomorphisms/")

        for key, graph in graphs_dict_total.items():
            graph_file = output_folder / f"analysis/isomorphisms/graphs/{key}.pdf"
            if not graph_file.is_file():
                graph_to_pdf(graph, key, "analysis/isomorphisms/graphs")

        iteration += 1
        nodes_types_set_list.append(nodes_types_str)


if __name__ == "__main__":
    designs_chosen = []
    for did, (dc, dt) in designs.items():
        if did in ["NewAxe_Cargo", "PickAxe", "TestQuad_Cargo"]:
            designs_chosen.append(dc)
    # predefined_nodes(designs_chosen)
    random_sampling_for_n()
