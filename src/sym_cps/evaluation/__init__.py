"""
File adapted from:
https://github.com/LOGiCS-Project/swri-simple-uam-example
"""

from pathlib import Path

from simple_uam import direct2cad
from sym_cps.evaluation.tools import polling_results, load_design, load_metadata, extract_results


def evaluate_design(design_json_path: Path,
                    metadata: Path | dict | None = None,
                    timeout: int = 800,
                    info_only: bool = False,
                    control_opt: bool = False):
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
        msg = direct2cad.gen_info_files.send(design, metadata=metadata)
    else:
        print("Processing design...")
        msg = direct2cad.process_design.send(design, metadata=metadata)
    print("Waiting for results...")
    result_path = polling_results(msg, timeout)
    print(f"Command completed. Results can be found at:{result_path}")
    # Obtain information from the result foleder
    if not info_only:
        return extract_results(result_path, control_opt = control_opt)
        #return extract_results("/Users/shengjungyu/shengjungyu/Research/UC_Berkeley/Research/LOGiCS/workspace/berkeley-cps-symbiotic-design/output/aws/results/process_design-2022-10-07-fhudp1f5qz.zip", control_opt = control_opt)
    else:
        return None
