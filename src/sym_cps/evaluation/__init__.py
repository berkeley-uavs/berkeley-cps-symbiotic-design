"""
File adapted from:
https://github.com/LOGiCS-Project/swri-simple-uam-example
"""
import json
from pathlib import Path

from simple_uam.direct2cad.actions.actors import process_design, gen_info_files
from simple_uam.client.watch import poll_results_backend

from sym_cps.evaluation.tools import extract_results, load_design, load_metadata, polling_results
from sym_cps.shared.paths import designs_folder


def evaluate_design(
        design_json_path: Path,
        metadata: Path | dict | None = None,
        timeout: int = 800,
        info_only: bool = False,
        control_opt: bool = False,
) -> dict:
    """Evaluate a design_swri.json provided at location 'design_json_path'
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
        msg = gen_info_files.send(design, metadata=metadata)
    else:
        print("Processing design...")
        msg = process_design.send(design, metadata=metadata)
        print("Hello")
        print(json.dumps(msg.asdict()))
    print("Waiting for results...")
    result_path = poll_results_backend(msg, timeout)  # polling_results(msg, timeout)
    print(f"Command completed. Results can be found at:{result_path}")
    # Obtain information from the result foleder
    if not info_only:
        return extract_results(result_path, control_opt=control_opt)
        # return extract_results("/Users/shengjungyu/shengjungyu/Research/UC_Berkeley/Research/LOGiCS/workspace/challenge_data/aws/results/process_design-2022-11-02-kvrbcwlwpg.zip", control_opt = control_opt)
    else:
        return None


if __name__ == '__main__':
    "Testing evaluation data"
    design_json_path = designs_folder / "NewAxe_Cargo" / "design_swri.json"
    evaluate_design(design_json_path)