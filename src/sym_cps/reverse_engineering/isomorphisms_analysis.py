import json
from collections import Counter, OrderedDict
from pathlib import Path

from sym_cps.shared.designs import designs
from sym_cps.shared.paths import summary_structure_path
from sym_cps.tools.my_io import save_to_file

designs_to_analyze = [d[0] for d in designs.values()]


def process_isomorphisms_summary_json(json_file_path: Path):
    structure_summary: dict = json.load(open(json_file_path))

    popular_node_keys = Counter()

    for structure, info in structure_summary["GLOBAL"].items():
        structrue_elements = structure.split("-")
        sorted_keys = sorted(results["KEYS"])
        key_string = "-".join(sorted_keys)
        popular_node_keys[key_string] = int(results["HITS"])

    pop_dict = OrderedDict(popular_node_keys.most_common())

    save_to_file(pop_dict, "popular_node_keys.json", "analysis")


if __name__ == "__main__":
    # process_isomorphisms_summary_json(summary_structure_path)
    process_isomorphisms_summary_json(summary_structure_path)
