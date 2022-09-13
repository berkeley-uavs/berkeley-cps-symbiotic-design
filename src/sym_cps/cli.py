"""Module that contains the command line application."""

import argparse
from numpy.ctypeslib import load_library
from sym_cps.examples.designs import export_design_json, load_design_json
from typing import List, Optional
from sym_cps.examples.library import *


def get_parser() -> argparse.ArgumentParser:
    """
    Return the CLI argument parser.

    Returns:
        An argparse parser.
    """
    return argparse.ArgumentParser(prog="sym-cps")


def run_parse_library() -> int:
    parse_library()
    return 0


def run_load_library() -> int:
    load_library()
    return 0


def run_export_design(args: Optional[List[str]] = None) -> int:
    parser = get_parser()
    opts = parser.parse_args(args=args)
    export_design_json(opts[0])
    return 0

def run_load_design_json(args: Optional[List[str]] = None) -> int:
    parser = get_parser()
    opts = parser.parse_args(args=args)
    load_design_json(opts[0])
    return 0


def example_with_parameters(args: Optional[List[str]] = None) -> int:
    parser = get_parser()
    opts = parser.parse_args(args=args)
    print(f"args: {opts}")  # noqa: WPS421 (side-effect in main is fine)
    return 0


