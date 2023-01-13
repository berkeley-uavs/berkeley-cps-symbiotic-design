import json
import operator
import os
import pickle
import random
import shutil
import string
from pathlib import Path

from sym_cps.grammar import AbstractGrid
from sym_cps.grammar.rules import generate_random_new_topology
from sym_cps.representation.design.abstract import AbstractDesign
from sym_cps.representation.tools.optimize import find_components
from sym_cps.shared.paths import designs_folder, stats_file_path, stats_folder, stats_speeds_file_path, \
    stats_file_txt_path, random_topologies_all_path
from sym_cps.tools.my_io import save_to_file
from sym_cps.tools.strings import get_speeds_from_metrics


def make_stats():
    designs_generated_stats, random_topologies_generated = get_all_stat()
    designs_in_folder = set(filter(lambda x: x[0].isdigit(), [f.name for f in list(Path(designs_folder).iterdir())]))

    """Not NONE score"""
    total_score = {}
    for design_id, scores in designs_generated_stats.items():
        vs = [v[0] for v in scores.values() if isinstance(v, list)]
        if len(vs) == 0:
            continue
        total_score[design_id] = sum(vs)

    sorted_total_score = dict(sorted(total_score.items(), key=operator.itemgetter(1), reverse=True))
    final_dictionary = {}
    for design_id, tot_score in sorted_total_score.items():
        all_scores = designs_generated_stats[design_id]
        all_scores["total"] = tot_score
        final_dictionary[design_id] = all_scores

    """Cleaning up folder"""
    non_zero_score = set(total_score.keys())
    designs_to_delete = designs_in_folder - non_zero_score
    designs_to_delete_hash = []
    for design_to_delete in designs_to_delete:
        for k, v in random_topologies_generated.items():
            if design_to_delete == v:
                designs_to_delete_hash.append(k)
        design_dir = Path(designs_folder / design_to_delete)
        print(f"Renaming {design_dir}")
        if os.path.exists(design_dir) and os.path.isdir(design_dir):
            shutil.move(design_dir, designs_folder / f"fail_{design_to_delete}")
    for k in designs_to_delete_hash:
        del random_topologies_generated[k]

    """Getting the designs with scores"""
    designs_in_folder = set(filter(lambda x: x.name[0].isdigit(), [f for f in list(Path(designs_folder).iterdir())]))

    designs_speeds_txt = ""
    designs_speeds: dict[str, list[float]] = {}
    for design_dir in designs_in_folder:
        speeds: list[float] = []
        for fdm_result_dir in list(Path(design_dir / "Results").iterdir()):
            if not fdm_result_dir.is_dir():
                continue
            metric_file_path = fdm_result_dir / "fdmTB" / "metrics.out"
            speeds.extend(get_speeds_from_metrics(metric_file_path))
        speeds.insert(0, max(speeds))
        designs_speeds[design_dir.name] = speeds
    sorted_designs_speeds = dict(sorted(designs_speeds.items(), key=operator.itemgetter(1), reverse=True))

    for design, speeds in sorted_designs_speeds.items():
        designs_speeds_txt += f"{speeds[0]}\t{design}\n"
    save_to_file(sorted_designs_speeds, absolute_path=stats_speeds_file_path, sort=False, overwrite=True)
    save_to_file(final_dictionary, absolute_path=stats_file_path, sort=False, overwrite=True)
    save_to_file(designs_speeds_txt, absolute_path=stats_file_txt_path, sort=False, overwrite=True)


def get_latest_evaluated_design_number() -> int:
    index = 0
    for path in Path(designs_folder).iterdir():
        if path.is_dir():
            path_split = str(path).split("__")
            # print(path_split)
            if len(path_split) > 1:
                try:
                    path_split_2 = str(path_split[0]).split("challenge_data/output/designs/")
                    first_n = int(path_split_2[1])
                    if first_n > index:
                        index = first_n
                except:
                    continue
    print(f"latest_index: {index}")
    return index


def generate_random_instance_id() -> str:
    return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(4))


def get_random_new_topology(design_tag, design_index, n_wings_max=-1, n_props_max=-1) -> AbstractDesign:
    new_design: AbstractDesign = generate_random_new_topology(
        design_tag=design_tag,
        design_index=design_index,
        max_right_num_wings=n_wings_max,
        max_right_num_rotors=n_props_max,
    )
    return new_design


def make_design(tag: str,
                wings_max=0,
                n_props_max=-1,
                optimize: bool = True):
    design_tag = f"grammar_{tag}"
    design_index = get_latest_evaluated_design_number()
    new_design: AbstractDesign = get_random_new_topology(design_tag, design_index + 1, wings_max, n_props_max)
    new_design.save()
    d_concrete = new_design.to_concrete()
    d_concrete.choose_default_components_for_empty_ones()
    if optimize:
        find_components(d_concrete)
    d_concrete.export_all()
    d_concrete.evaluate()


def evaluate_grid(grid_file_path: Path, optimize: bool = True):
    with open(grid_file_path, "rb") as pickle_file:
        abstract_grid: AbstractGrid = pickle.load(pickle_file)
        print(f"Building AbstractDesign")
        new_design = AbstractDesign(abstract_grid.name)
        new_design.parse_grid(abstract_grid)
        d_concrete = new_design.to_concrete()
        d_concrete.choose_default_components_for_empty_ones()
        if optimize:
            find_components(d_concrete)
        d_concrete.export_all()
        d_concrete.evaluate()


def store_all_topology_generated():
    designs_in_folder = set(filter(lambda x: "grammar" in x.name, [f for f in list(Path(designs_folder).iterdir())]))

    random_topologies_generated = {}
    for design_path in designs_in_folder:
        file = design_path / "grid.dat"
        if file.is_file():
            with open(file, "rb") as pickle_file:
                grid: AbstractGrid = pickle.load(pickle_file)
                new_design = AbstractDesign(design_path.name)
                new_design.parse_grid(grid)
                random_topologies_generated[new_design.id] = design_path.name

    save_to_file(random_topologies_generated, absolute_path=random_topologies_all_path, overwrite=False)



def get_all_stat() -> tuple[dict, dict]:
    if not stats_folder.is_dir():
        return {}, {}
    random_designs_stats_files = list(
        filter(lambda x: "random_designs_stats" in str(x), list(Path(stats_folder).iterdir()))
    )
    random_topologies_generated_files = list(
        filter(
            lambda x: "random_topologies_generated" in str(x), list(Path(stats_folder).iterdir())
        )
    )
    print(random_designs_stats_files)
    print(random_topologies_generated_files)
    random_designs_stats_dict = {}
    random_topologies_generated_dict = {}

    for stat_file in random_designs_stats_files:
        stat_file_dict: dict = json.load(open(stat_file))
        random_designs_stats_dict.update(stat_file_dict)

    for gen_file in random_topologies_generated_files:
        gen_file_dict: dict = json.load(open(gen_file))
        random_topologies_generated_dict.update(gen_file_dict)

    return random_designs_stats_dict, random_topologies_generated_dict


def optimize_designs():
    designs_in_folder = set(
        filter(lambda x: not x.contains("_comp_opt"), [f.name for f in list(Path(designs_folder).iterdir())])
    )

    print(f"Designs not optimized: {designs_in_folder}")

    for design_to_opt in designs_in_folder:
        grid_file = Path(design_to_opt) / "grid.dat"
        evaluate_grid(grid_file, optimize=True)



def get_design_id(name: str):
    first = name.split("__")[0]
    last = name.split("__")[1]

    index = first.split("_")
    last = last.split("_comp_opt")[0]
    if len(index) == 2:
        index = index[1]
    else:
        index = index[0]

    return f"{index}__grammar_{last}"


def cleanup_folders():
    failed_designs = set(filter(lambda x: "fail" in x.name, [f for f in list(Path(designs_folder).iterdir())]))
    not_failed = set(filter(lambda x: "fail" not in x.name and "grammar" in x.name, [f for f in list(Path(designs_folder).iterdir())]))

    design_ids: dict[str, list[Path]] = {}

    for design_path in failed_designs | not_failed:
        design_id = get_design_id(design_path.name)
        if design_id not in design_ids.keys():
            design_ids[design_id] = []
        design_ids[design_id].append(design_path)

    copy_dict: dict[Path, Path] = {}
    delete_dir: list[Path] = []

    for design_id, paths in design_ids.items():
        for dir in paths:
            for file in dir.iterdir():
                if file.name == "grid.dat":
                    for dir_2 in paths:
                        if dir_2 != dir:
                            copy_dict[dir] = dir_2
                            delete_dir.append(dir)

    for source, destination in copy_dict.items():
        if source.is_dir():
            shutil.copytree(source, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(source, destination)

    for dir in delete_dir:
        shutil.rmtree(dir)

    for folder in designs_folder.iterdir():
        if folder.is_dir():
            new_name = folder.name.replace("_comp_opt", "")
            os.rename(folder, designs_folder / new_name)



if __name__ == "__main__":
    make_stats()
    # store_all_topology_generated()
    # store_all_topology_generated()
    # cleanup_folders()
