# type: ignore
import json
from copy import deepcopy

from sym_cps.representation.design.concrete import DConcrete
from sym_cps.representation.design.topology import DTopology
from sym_cps.representation.tools.parsers.parsing_designs import parse_design_from_design_swri
from sym_cps.shared.paths import designs_folder
from sym_cps.tools.my_io import save_to_file
from sym_cps.tools.persistance import load


def export_design_json(design_name: str = "Trowel", designs_dat_file: str = "designs.dat"):
    """Produce the json file representing the design"""
    designs: dict[str, tuple[DConcrete, DTopology]] = load(designs_dat_file)  # type: ignore

    d_concrete = designs[design_name][0]

    save_to_file(
        str(json.dumps(d_concrete.to_design_swri)),
        file_name=f"design_swri.json",
        absolute_path=designs_folder / d_concrete.name,
    )
    print(f"{design_name} exported to json")


def load_design_json(design_name: str = "Trowel", library_dat_file: str = "library.dat"):
    """Load a design from json format"""
    """BUG: FIXME: Does not work with new designs, e.g. NewAxe"""

    c_library: Library = load(library_dat_file)  # type: ignore

    design_swri_path = designs_folder / design_name / "design_swri.json"

    d_concrete: DConcrete = parse_design_from_design_swri(path=design_swri_path, library=c_library)
    d_topology: DTopology = DTopology.from_concrete(d_concrete)

    print(d_concrete)
    print(d_topology)

    print(f"{design_name} imported from json")


def modify_parameters_to_design(design_name: str = "Trowel", designs_dat_file: str = "designs.dat"):
    designs: dict[str, tuple[DConcrete, DTopology]] = load(designs_dat_file)  # type: ignore

    d_concrete = designs[design_name][0]

    modified_design = deepcopy(d_concrete)
    modified_design.name = design_name + "_new_parameters"

    new_params = {
        "Param_0": 1650,
        "Param_1": 2000,
        "Param_10": 45,
        "Param_11": 10000,
        "Param_12": 1000,
        "Param_14": 4500,
        "Param_15": 25,
        "Param_16": 790,
        "Param_17": 210,
        "Param_18": -210,
        "Param_19": 315,
        "Param_2": 12,
        "Param_3": 1000,
        "Param_4": 150,
        "Param_5": 2000,
        "Param_6": 1520,
        "Param_7": 200,
        "Param_8": 300,
        "Param_9": 150,
    }

    for param, value in new_params.items():
        modified_design.design_parameters[param].value = value

    save_to_file(
        str(modified_design),
        file_name=f"DConcrete",
        absolute_path=designs_folder / modified_design.name,
    )
    print(f"A new design {modified_design.name} has been generated from {design_name} and modifying its parameters")


if __name__ == "__main__":
    export_design_json()
    load_design_json()
    modify_parameters_to_design()
