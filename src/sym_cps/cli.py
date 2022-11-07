"""Module that contains the command line application."""
import argparse
from pathlib import Path
from typing import List, Optional

from sym_cps.examples.library import export_library, generate_tables, analysis
from sym_cps.representation.design.concrete import DConcrete
from sym_cps.shared.paths import data_folder, output_folder
from sym_cps.tools.update_library import export_all_designs, update_dat_files_and_export
from sym_cps.evaluation import evaluate_design

def _parse_design(args: Optional[List[str]] = None) -> DConcrete:
    parser = argparse.ArgumentParser(prog="sym-cps")
    parser.add_argument("design_file", type=str, help="Specify the design json to parse")
    opts = parser.parse_args(args=args)
    print(f"args: {opts}")
    print(opts.design_file)
    file = data_folder / "custom_designs" / opts.design_file
    print(f"Parsing file {file}")
    if file.suffix == "":
        file_str = str(file)
        file_str += ".json"
        file = Path(file_str)
    from sym_cps.grammar.topology import AbstractTopology
    from sym_cps.representation.design.concrete import DConcrete
    abstract_topology = AbstractTopology.from_json(file)
    return DConcrete.from_abstract_topology(abstract_topology)

def update_all() -> int:
    update_dat_files_and_export()
    export_library()
    # generate_tables()
    analysis()
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
    parser.add_argument("design_name", type=str, help="Specify the design name to evaluate the existing design_swri.json")
    opts = parser.parse_args(args=args)
    print(f"args: {opts}")
    print(opts.design_name)
    design_json_path = output_folder / "designs"/ opts.design_name/ "design_swri.json"
    ret = evaluate_design(
        design_json_path=design_json_path, metadata={"extra_info": "full evaluation example"}, timeout=800
    )
    print(ret)
    return 0

