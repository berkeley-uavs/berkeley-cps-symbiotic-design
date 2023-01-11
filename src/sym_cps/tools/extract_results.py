import json
from collections import Counter
from pathlib import Path

from sym_cps.shared.paths import stats_folder
from sym_cps.tools.my_io import save_to_file


def merge_all_results():
    if not stats_folder.is_dir():
        return {}, {}
    random_designs_stats_files = list(
        filter(lambda x: "random_designs_stats" in str(x), list(Path(stats_folder).iterdir()))
    )
    print(random_designs_stats_files)

    results = {}
    scores = Counter()

    zeros = 0
    all = 0

    for stat_file in random_designs_stats_files:
        all += 1
        stat_file_dict: dict = json.load(open(stat_file))
        for k, scores in stat_file_dict.items():
            if scores["fdmResult7"] is not None:
                tot = []
                if scores["fdmResult7"][0] == 0:
                    zeros += 1
                if scores["fdmResult7"][0] == 2569:
                    print(k)
                for sk, score in scores.items():
                    if sk != "status":
                        tot.append(score[0])
                scores[k] = max(tot)
                # print(f"{k} -> {max(tot)}")
                # print(f"{k} -> {tot}")
                results.update(stat_file_dict)

    save_to_file(results, "merged_results.json")
    save_to_file(scores, "top_scores.json")

    non_zero = all-zeros
    print(all)
    print(non_zero)
    print(non_zero/all)

if __name__ == '__main__':
    merge_all_results()
