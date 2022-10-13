"""
File adapted from:
https://github.com/LOGiCS-Project/swri-simple-uam-example
"""

import argparse
import json
from pathlib import Path

from simple_uam import direct2cad
from simple_uam.worker import has_backend

from sym_cps.evaluation.tools import (
    get_result_archive_path,
    get_zip_metadata,
    load_design,
    load_metadata,
    wait_on_result,
    watch_results_dir,
)


def get_args():
    """
    Creates a parser and returns the arguments for this utility.
    """

    parser = argparse.ArgumentParser(description="Process a design")
    parser.add_argument(
        "-results_dir",
        type=Path,
        help="The directory that will be checked when looking for new results.",
    )
    parser.add_argument(
        "-design_file",
        type=Path,
        help="The design file to process",
    )
    parser.add_argument(
        "-m",
        "--metadata",
        default=None,
        help="Metadata to include with the operation, becomes part of metadata.json in the result.",
    )
    parser.add_argument(
        "-c",
        "--command",
        choices=["info", "process"],
        default="info",
        help="Which command to perform: 'info' = gen info files, 'process' = process design.",
    )
    parser.add_argument(
        "-w",
        "--watch",
        choices=["best", "backend", "polling"],
        default="best",
        help="How to wait for results, via backend, polling, or best available.",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        default=600,
        help="Timeout, in seconds, before giving up on the command.",
    )
    return parser.parse_args()


def cli():
    args = get_args()

    # Load the design from file
    print("Loading Design")
    design = load_design(args.design_file)

    # Load the metadata from file
    print("Loading Metadata (if provided)")
    metadata = load_metadata(args.metadata)

    # Send the design to worker
    print("Sending Design to Broker")
    msg = None
    if args.command == "info":
        print("Generating...")
        msg = direct2cad.gen_info_files.send(design, metadata=metadata)
    elif args.command == "process":
        print("Processing...")
        msg = direct2cad.process_design.send(design, metadata=metadata)

    # Wait for the result to appear
    print("Waiting for results")
    use_backend = (args.watch == "backend") or (has_backend() and args.watch != "polling")
    result_archive = None

    ### EVERYTHING BELOW THIS POINT IS AN EXAMPLE ###
    ###   THAT SHOULDN'T BE USED IN PRODUCTION    ###

    if use_backend:

        # We get completion notifications from the backend so use that
        result = wait_on_result(msg, timeout=args.timeout)
        result_archive = get_result_archive_path(result, args.results_dir)

        print("Retrieved result from backend:")
        print(json.dumps(result, indent="  "))

    else:

        # No backend, so watch for changes in the results dir
        result_archive = watch_results_dir(msg, args.results_dir, timeout=args.timeout)
        result = get_zip_metadata(result_archive)

        print("Result archive found in results dir w/ metadata:")
        print(json.dumps(result, indent="  "))

    print("Command completed. Results can be found at:")
    print(result_archive)
