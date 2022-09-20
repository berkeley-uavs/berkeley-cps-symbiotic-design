from pathlib import Path

from simple_uam import direct2cad
from sym_cps.evaluation.tools import polling_results


def evaluate_design(design_json_path: Path, metadata: str | None = None, timeout: int = 800):
    """ Evaluate a design_swri.json provided at location 'design_json_path'
    Metadata to include with the operation, becomes part of metadata.json in the result.
    """
    print("Processing design started...")
    msg = direct2cad.process_design.send(str(design_json_path), metadata=metadata)
    print("Waiting for results...")
    result_path = polling_results(msg, timeout)
    print(f"Command completed. Results can be found at:{result_path}")


def generate_info_files(design_json_path: Path, metadata: str | None = None, timeout: int = 800):
    """ Evaluate a design_swri.json provided at location 'design_json_path'
        Metadata to include with the operation, becomes part of metadata.json in the result.
        """
    print("Generating info files started...")
    msg = direct2cad.gen_info_files.send(str(design_json_path), metadata=metadata)
    print("Waiting for results")
    result_path = polling_results(msg, timeout)
    print(f"Command completed. Results can be found at:{result_path}")
