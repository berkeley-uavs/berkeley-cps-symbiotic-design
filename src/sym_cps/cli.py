"""Module that contains the command line application."""
import argparse
from pathlib import Path
from typing import List, Optional

from sym_cps.grammar.topology import AbstractTopology
from sym_cps.representation.design.concrete import DConcrete
from sym_cps.shared.paths import data_folder
from sym_cps.tools.update_library import export_all_designs, update_dat_files_and_export


def update_all() -> int:
    update_dat_files_and_export()
    return 0


def export_designs() -> int:
    export_all_designs()
    return 0


def load_custom_design(args: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="sym-cps")
    parser.add_argument("design_file", type=str, help="Specify the design json to parse")
    opts = parser.parse_args(args=args)
    print(f"args: {opts}")
    print(opts.design_file)
    file = data_folder / "custom_designs" / opts.design_file
    if file.suffix == "":
        file_str = str(file)
        file_str += ".json"
        file = Path(file_str)
    abstract_topology = AbstractTopology.from_json(file)
    dconcrete = DConcrete.from_abstract_topology(abstract_topology)
    dconcrete.export_all()
    # dtopology = DTopology.from_concrete(dconcrete)
    # designs[dconcrete.name] = (dconcrete, dtopology)
    # update_dat_designs()
    return 0
