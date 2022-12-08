import json
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
from sym_cps.shared.paths import designs_folder, stats_file_path, stats_folder
from sym_cps.tools.my_io import save_to_file


def _stats_make():
    designs_generated_stats, random_topologies_generated = get_all_stat()
    designs_in_folder = set(filter(lambda x: x[0].isdigit(), [f.name for f in list(Path(designs_folder).iterdir())]))
    completed_designs = set(designs_generated_stats.keys())

    designs_to_delete = designs_in_folder - completed_designs
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

    save_to_file(designs_generated_stats, absolute_path=stats_file_path)


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


def make_design(tag: str, wings_max=0, n_props_max=-1):
    design_tag = f"grammar_{tag}"
    design_index = get_latest_evaluated_design_number()
    new_design: AbstractDesign = get_random_new_topology(design_tag, design_index + 1, wings_max, n_props_max)
    new_design.save()
    d_concrete = new_design.to_concrete()
    d_concrete.choose_default_components_for_empty_ones()
    d_concrete.export_all()
    d_concrete.evaluate()


def evaluate_grid(grid_file_path: Path, optimize: bool = True):
    with open(grid_file_path, "rb") as pickle_file:
        abstract_grid: AbstractGrid = pickle.load(pickle_file)
        print(f"Building AbstractDesign")
        new_design = AbstractDesign(abstract_grid.name)
        new_design.parse_grid(abstract_grid)
        d_concrete = new_design.to_concrete()
        if optimize:
            find_components(d_concrete)
        d_concrete.export_all()
        d_concrete.evaluate()



def get_all_stat() -> tuple[dict, dict]:
    random_designs_stats_files = list(
        filter(lambda x: "random_designs_stats" in x, list(str(Path(stats_folder).iterdir())))
    )
    random_topologies_generated_files = list(
        filter(
            lambda x: "random_topologies_generated" in x, list(str(Path(stats_folder).iterdir()))
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
        optimize_design(grid_file)

#
# n_designs = 20
# n_wings_max = 0
# n_prop_max = -1
#
# if __name__ == "__main__":
#
#     index = get_latest_evaluated_design_number()
#
#     random_call_id = generate_random_instance_id()
#
#     for i in range((index + 1), (index + n_designs + 1)):
#         print(f"Random iteration {i}")
#         design_tag = f"directions_props_grammar_{random_call_id}"
#         design_index = i
#
#         new_design: AbstractDesign = get_random_new_topology(design_tag, design_index, n_wings_max, n_prop_max)
#
#         new_design.save(folder_name=f"designs/{new_design.name}")
#
#         d_concrete = new_design.to_concrete()
#
#         d_concrete.choose_default_components_for_empty_ones()
#
#         d_concrete.export_all()
#
#         find_components(d_concrete)
#
#         d_concrete.export_all()
#
#         save_to_file(d_concrete, file_name="d_concrete", folder_name=f"designs/{self.name}")
#
#         print(f"Design {d_concrete.name} generated")
#         print(f"Evaluating..")
#         d_concrete.evaluate()
