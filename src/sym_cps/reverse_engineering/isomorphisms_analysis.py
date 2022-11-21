import json
from collections import Counter, OrderedDict
from pathlib import Path

from sym_cps.shared.designs import designs
from sym_cps.shared.paths import isomorphisms_data_path
from sym_cps.tools.my_io import save_to_file

designs_to_analyze = [d[0] for d in designs.values()]


def process_isomorphisms_summary_json(json_file_path: Path):
    structure_summary: dict = json.load(open(json_file_path))

    popular_node_keys = Counter()

    for iteration, results in structure_summary.items():
        sorted_keys = sorted(results["KEYS"])
        key_string = "-".join(sorted_keys)
        popular_node_keys[key_string] = int(results["HITS"])

    pop_dict = OrderedDict(popular_node_keys.most_common())

    # json.dumps(OrderedDict([("b", 2), ("a", 1)]))

    save_to_file(pop_dict, "popular_node_keys.json", "analysis")


def process_isomorphisms_darta_json(json_file_path: Path):
    isomorphisms_data: dict = json.load(open(json_file_path))

    global_isos = isomorphisms_data["GLOBAL"]
    local_isos = isomorphisms_data["LOCAL"]

    global_isos_poular = Counter()
    local_isos_poular = Counter()

    for iteration, results in structure_summary.items():
        sorted_keys = sorted(results["KEYS"])
        key_string = "-".join(sorted_keys)
        popular_node_keys[key_string] = int(results["HITS"])

    pop_dict = OrderedDict(popular_node_keys.most_common())

    # json.dumps(OrderedDict([("b", 2), ("a", 1)]))

    save_to_file(pop_dict, "popular_node_keys.json", "analysis")


if __name__ == "__main__":
    # process_isomorphisms_summary_json(summary_structure_path)
    process_isomorphisms_darta_json(isomorphisms_data_path)
