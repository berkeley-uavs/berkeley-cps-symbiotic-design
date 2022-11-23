from __future__ import annotations

import json
import random
from itertools import product

from sym_cps.isomorphisms.tools import find_isomorphisms, get_subgraph, is_isomorphism_present
from sym_cps.representation.design.concrete import DConcrete
from sym_cps.shared.designs import designs
from sym_cps.shared.paths import output_folder, popular_nodes_keys_path
from sym_cps.tools.graphs import graph_to_pdf
from sym_cps.tools.my_io import save_to_file


def find_isos(
    designs_to_decompose: list[DConcrete], key_nodes: list[str] | None = None
) -> tuple[dict[str, list[dict]], dict[str, list[dict]], dict, dict]:
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
        return {}, {}, {}, {}

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
    for i in range(n_nodes_min, n_nodes_max + 1):
        proposals = []
        for elem in subgraphs:
            if i in elem.keys():
                proposals.append(elem[i])
        if len(proposals) > 0:
            candiates[i] = list(product(*proposals))

    global_iso_graphs = {}
    local_iso_graphs = {}
    global_iso = {}
    local_iso = {}
    for n_nodes, combinations in candiates.items():
        if len(combinations) <= 1:
            print("no combinations same length")
            return {}, {}, {}, {}
        for combination in combinations:
            isomorphisms_summary, iso_graphs, all_elements = find_isomorphisms(combination)
            if all_elements:
                global_iso_graphs.update(iso_graphs)
                for iso_key, structures in isomorphisms_summary.items():
                    if iso_key not in global_iso.keys():
                        global_iso[iso_key] = structures
                    for elem in isomorphisms_summary[iso_key]:
                        if elem not in global_iso[iso_key]:
                            global_iso[iso_key].append(elem)
            else:
                local_iso_graphs.update(iso_graphs)
                for iso_key, structures in isomorphisms_summary.items():
                    if iso_key not in local_iso.keys():
                        local_iso[iso_key] = structures
                    for elem in isomorphisms_summary[iso_key]:
                        if elem not in local_iso[iso_key]:
                            local_iso[iso_key].append(elem)

    print(f"Found {len(local_iso)} local isomorphisms and {len(global_iso)} global ones")
    return local_iso, global_iso, global_iso_graphs, local_iso_graphs


def explore_structures(designs: list[DConcrete], key_nodes: list[str]):
    local_iso, global_iso, global_iso_graphs, local_iso_graphs = find_isos(designs, key_nodes)

    summary = {"LOCAL": {}, "GLOBAL": {}}

    for structure_key, structure in local_iso.items():
        if structure_key not in summary["LOCAL"]:
            summary["LOCAL"] = {structure_key: structure}
        else:
            summary["LOCAL"] = {structure_key: structure}
            for new_elem in structure:
                if new_elem not in summary["LOCAL"][structure_key]:
                    summary["LOCAL"][structure_key].append(new_elem)

    for structure_key, structure in global_iso.items():
        if structure_key not in summary["GLOBAL"]:
            summary["GLOBAL"] = {structure_key: structure}
        else:
            summary["GLOBAL"] = {structure_key: structure}
            for new_elem in structure:
                if new_elem not in summary["GLOBAL"][structure_key]:
                    summary["GLOBAL"][structure_key].append(new_elem)

    return summary, global_iso_graphs, local_iso_graphs


#
# def predefined_nodes(designs_chosen):
#     key_nodes = ["BatteryController", "Tube", "Hub2", "Hub3", "Hub4", "Hub5", "Hub6"]
#     return explore_structures(designs_chosen, key_nodes)
#
#
# def random_sampling(designs_chosen, nodes_types):
#     subset = random.sample(nodes_types, random.randint(1, len(nodes_types)))
#     print(f"Node keys: {subset}")
#     subset = ["BatteryController", "Tube", "Hub2", "Hub3", "Hub4", "Hub5", "Hub6"]
#     return explore_structures(designs_chosen, subset)


popular_nodes: dict = json.load(open(popular_nodes_keys_path))
popular_nodes_list: list = list(popular_nodes.keys())


def random_sampling_for_n(iterations: int = 10000000):
    designs_chosen = []
    for did, (dc, dt) in designs.items():
        if did in ["NewAxe_Cargo", "PickAxe", "TestQuad_Cargo"]:
            designs_chosen.append(dc)
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

    global_graphs_dict_total = {}
    local_graphs_dict_total = {}

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
        summary, global_iso_graphs, local_iso_graphs = explore_structures(designs_chosen, nodes_types_set)
        global_graphs_dict_total.update(global_iso_graphs)
        local_graphs_dict_total.update(local_iso_graphs)

        for structure_key, structures in summary["LOCAL"].items():
            if structure_key not in total_summary["LOCAL"].keys():
                total_summary["LOCAL"][structure_key] = {"VARIATIONS": [], "KEYS": [], "COUNT": 0}
                total_summary["LOCAL"][structure_key]["VARIATIONS"] = structures
                total_summary["LOCAL"][structure_key]["KEYS"] = [nodes_types_str]
                total_summary["LOCAL"][structure_key]["COUNT"] = len(structures)
            else:
                for elem in structures:
                    if elem not in total_summary["LOCAL"][structure_key]["VARIATIONS"]:
                        total_summary["LOCAL"][structure_key]["VARIATIONS"].append(elem)
                        total_summary["LOCAL"][structure_key]["COUNT"] += 1
        for structure_key, structures in summary["GLOBAL"].items():
            if structure_key not in total_summary["GLOBAL"].keys():
                total_summary["GLOBAL"][structure_key] = {"VARIATIONS": [], "KEYS": [], "COUNT": 0}
                total_summary["GLOBAL"][structure_key]["VARIATIONS"] = structures
                total_summary["GLOBAL"][structure_key]["KEYS"] = [nodes_types_str]
                total_summary["GLOBAL"][structure_key]["COUNT"] = len(structures)
            else:
                for elem in structures:
                    if elem not in total_summary["GLOBAL"][structure_key]["VARIATIONS"]:
                        total_summary["GLOBAL"][structure_key]["VARIATIONS"].append(elem)
                        total_summary["GLOBAL"][structure_key]["COUNT"] += 1

        save_to_file(total_summary, "structure_summary.json", f"analysis/isomorphisms/")

        for key, graph in global_graphs_dict_total.items():
            graph_file = output_folder / f"analysis/isomorphisms/graphs/global/{key}.pdf"
            if not graph_file.is_file():
                graph_to_pdf(graph, key, "analysis/isomorphisms/graphs/global")
        for key, graph in local_graphs_dict_total.items():
            graph_file = output_folder / f"analysis/isomorphisms/graphs/local/{key}.pdf"
            if not graph_file.is_file():
                graph_to_pdf(graph, key, "analysis/isomorphisms/graphs/local")

        iteration += 1
        nodes_types_set_list.append(nodes_types_str)


if __name__ == "__main__":
    designs_chosen = []
    for did, (dc, dt) in designs.items():
        if did in ["NewAxe_Cargo", "PickAxe", "TestQuad_Cargo"]:
            designs_chosen.append(dc)
    random_sampling_for_n()
