import json
import os
import random
import shutil
import string
from pathlib import Path

from sym_cps.grammar.rules import generate_random_new_topology
from sym_cps.representation.design.abstract import AbstractDesign
from sym_cps.representation.tools.optimize import find_components
from sym_cps.shared.paths import designs_folder, designs_generated_stats_path, random_topologies_generated_path
from sym_cps.tools.my_io import save_to_file


def _stats_cleanup():
    designs_generated_stats: dict = json.load(open(designs_generated_stats_path))
    random_topologies_generated: dict = json.load(open(random_topologies_generated_path))
    designs_in_folder = set(filter(lambda x: x[0].isdigit(), [f.name for f in list(Path(designs_folder).iterdir())]))
    completed_designs = set(designs_generated_stats.keys())

    designs_to_delete = designs_in_folder - completed_designs
    designs_to_delete_hash = []

    for design_to_delete in designs_to_delete:
        for k, v in random_topologies_generated.items():
            if design_to_delete == v:
                designs_to_delete_hash.append(k)
        design_dir = Path(designs_folder / design_to_delete)
        print(f"Deleting {design_dir}")
        if os.path.exists(design_dir) and os.path.isdir(design_dir):
            shutil.move(design_dir, designs_folder / f"fail_{design_to_delete}")

    for k in designs_to_delete_hash:
        del random_topologies_generated[k]

    save_to_file(designs_generated_stats, absolute_path=designs_generated_stats_path)
    save_to_file(random_topologies_generated, absolute_path=random_topologies_generated_path)


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


n_designs = 20
n_wings_max = 0
n_prop_max = -1

if __name__ == "__main__":
    _stats_cleanup()

    index = get_latest_evaluated_design_number()

    random_call_id = generate_random_instance_id()

    for i in range((index + 1), (index + n_designs + 1)):
        print(f"Random iteration {i}")
        design_tag = f"directions_props_grammar_{random_call_id}"
        design_index = i

        new_design: AbstractDesign = get_random_new_topology(design_tag, design_index, n_wings_max, n_prop_max)

        new_design.save(folder_name=f"designs/{new_design.name}")

        d_concrete = new_design.to_concrete()

        d_concrete.choose_default_components_for_empty_ones()

        d_concrete.export_all()

        find_components(d_concrete)

        d_concrete.export_all()

        save_to_file(d_concrete, file_name="d_concrete", folder_name=f"designs/{self.name}")

        print(f"Design {d_concrete.name} generated")
        print(f"Evaluating..")
        d_concrete.evaluate()
