"""Module that contains the command line application."""
import argparse
import pickle
from pathlib import Path
from typing import List, Optional

from sym_cps.evaluation import evaluate_design
from sym_cps.examples.library import export_library
from sym_cps.grammar.rules import AbstractGrid
from sym_cps.representation.design.abstract import AbstractDesign
from sym_cps.representation.design.concrete import DConcrete
from sym_cps.representation.design.human import HumanDesign
from sym_cps.shared.paths import aws_folder, data_folder
from sym_cps.tools.update_library import export_all_designs, update_dat_files_and_export


def _parse_design(args: Optional[List[str]] = None) -> DConcrete:
    parser = argparse.ArgumentParser(prog="sym-cps")
    parser.add_argument("--abstract_json", type=str, help="Specify the abstract json to parse")
    parser.add_argument("--grid", type=str, help="Specify the grid dat file")
    opts = parser.parse_args(args=args)
    print(f"args: {opts}")
    if opts.abstract_json is not None:
        file = data_folder / "custom_designs" / opts.abstract_json
        print(f"Parsing file {file}")
        if file.suffix == "":
            file_str = str(file)
            file_str += ".json"
            file = Path(file_str)
        human_topology = HumanDesign.from_json(file)
        return human_topology.to_concrete()
    elif opts.grid is not None:
        file = data_folder / "custom_designs" / opts.grid
        print(f"Parsing file {file}")
        if file.suffix == "":
            file_str = str(file)
            file_str += ".dat"
            file = Path(file_str)
        with open(file, 'rb') as pickle_file:
            abstract_grid: AbstractGrid = pickle.load(pickle_file)
            new_design = AbstractDesign(abstract_grid.name)
            return new_design.to_concrete()

    raise AttributeError


def update_all() -> int:
    update_dat_files_and_export()
    export_library()

    from sym_cps.reverse_engineering.parameters_analysis import library_analysis, parameter_analysis

    library_analysis()
    parameter_analysis()
    # TODO: FIX BUG IN fix_connecotrs_mapping, chaning the order of connectors
    # fix_connectors_mapping()
    # generate_tables()
    # analysis()
    return 0


def export_designs() -> int:
    export_all_designs()
    return 0


def load_custom_design(args: Optional[List[str]] = None) -> int:
    dconcrete = _parse_design(args)
    dconcrete.export_all()
    return 0


def evaluate_abstract_design(args: Optional[List[str]] = None) -> int:
    dconcrete = _parse_design(args)
    dconcrete.export_all()
    dconcrete.evaluate()
    return 0


def evaluate_design_swri(args: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="sym-cps")
    parser.add_argument(
        "design_name", type=str, help="Specify the design name to evaluate the existing design_swri.json"
    )
    opts = parser.parse_args(args=args)
    print(f"args: {opts}")
    print(opts.design_name)
    design_json_path = aws_folder / "examples" / opts.design_name / "design_swri.json"
    # output_folder / "designs" / opts.design_name / "design_swri.json"
    ret = evaluate_design(
        design_json_path=design_json_path, metadata={"extra_info": "full evaluation example"}, timeout=800
    )
    print(ret)
    return 0


if __name__ == '__main__':
    # dconcrete = _parse_design(["--abstract_json=grid/test_quad_cargo_test"])
    dconcrete = _parse_design(["--grid=grid/test_quad_cargo_grid.dat"])
    dconcrete.export_all()