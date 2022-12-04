"""
File adapted from:
https://github.com/LOGiCS-Project/swri-simple-uam-example
"""
import json
from pathlib import Path

from simple_uam.client.inputs import load_study_params
from simple_uam.client.watch import poll_results_backend
from simple_uam.direct2cad.actions.actors import gen_info_files, process_design

from sym_cps.evaluation.tools import extract_results, load_design, load_metadata, polling_results
from sym_cps.shared.paths import default_study_params_path, designs_folder


def evaluate_design(
    design_json_path: Path,
    study_params: Path | None | list[dict[str, str]] = None,
    metadata: Path | dict | None = None,
    timeout: int = 800,
    info_only: bool = False,
    control_opt: bool = False,
) -> dict:
    """Evaluate a design_swri_orog.json provided at location 'design_json_path'
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
        if study_params is not None:
            if isinstance(study_params, Path):
                study_params = load_study_params(study_params=study_params)
        else:
            study_params = load_study_params(study_params=default_study_params_path)
        msg = process_design.send(design, metadata=metadata, compile_args={"srcs": None}, study_params=study_params)
        # print(json.dumps(msg.asdict(), indent=2, sort_keys=True))
    print("Waiting for results...")
    result_path = polling_results(msg, timeout)  # poll_results_backend(msg, timeout)  #
    print(f"Command completed. Results can be found at:{result_path}")
    # Obtain information from the result foleder
    if not info_only:
        return extract_results(result_path, control_opt=control_opt)
        # return extract_results("/Users/shengjungyu/shengjungyu/Research/UC_Berkeley/Research/LOGiCS/workspace/challenge_data/aws/results/process_design-2022-11-02-kvrbcwlwpg.zip", control_opt = control_opt)
    else:
        return None


if __name__ == "__main__":
    "Testing evaluation data"
    # design_json_path = designs_folder / "NewAxe_Cargo" / "design_swri_orog.json"
    # design_json_path = "/Users/pier/Projects/challenge_data/output/designs/random_design_0/design_swri.json"
    design_json_path = designs_folder / "NewAxe_Cargo" / "design_swri_hor_hole.json"
    print(evaluate_design(design_json_path))
