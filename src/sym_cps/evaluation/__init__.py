from pathlib import Path

from simple_uam import direct2cad
from sym_cps.evaluation.tools import polling_results, load_design, load_metadata


def evaluate_design(design_json_path: Path,
                    metadata: Path | dict | None = None,
                    timeout: int = 800,
                    info_only: bool = False):
    """ Evaluate a design_swri.json provided at location 'design_json_path'
    Metadata to include with the operation, becomes part of metadata.json in the result.
    """
    print(f"Input file: {design_json_path}")
    # Load the design from file
    print("Loading Design")
    design = load_design(design_json_path)
    # Load the metadata from file
    print("Loading Metadata (if provided)")
    metadata = load_metadata(metadata)
    # Send the design to worker
    print("Sending Design to Broker")
    if info_only:
        print("Generating info...")
        msg = direct2cad.gen_info_files.send(str(design_json_path), metadata=metadata)
    else:
        print("Processing design...")
        msg = direct2cad.process_design.send(design, metadata=metadata)
    print("Waiting for results...")
    result_path = polling_results(msg, timeout)
    print(f"Command completed. Results can be found at:{result_path}")
