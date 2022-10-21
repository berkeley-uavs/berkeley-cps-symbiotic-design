"""Module that contains the command line application."""

import argparse
from typing import List, Optional

from sym_cps.tools.update_library import update_dat_files_and_export, export_all_designs


def get_parser() -> argparse.ArgumentParser:
    """
    Return the CLI argument parser.

    Returns:
        An argparse parser.
    """
    return argparse.ArgumentParser(prog="sym-cps")


def example_with_parameters(args: Optional[List[str]] = None) -> int:
    parser = get_parser()
    opts = parser.parse_args(args=args)
    print(f"args: {opts}")  # noqa: WPS421 (side-effect in main is fine)
    return 0


def update_all() -> int:
    update_dat_files_and_export()


def export_designs() -> int:
    export_all_designs()
