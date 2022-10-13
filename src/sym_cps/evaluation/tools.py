"""
File adapted from:
https://github.com/LOGiCS-Project/swri-simple-uam-example
"""

import json
import time
import zipfile
from pathlib import Path
from typing import Optional, Union

import dramatiq

from sym_cps.shared.paths import aws_folder, fdm_extract_folder


def load_design(design_file: Path) -> object:
    """
    Loads a design from file.

    Arguments:
      design_file: Path to the design file
    """
    with Path(design_file).open("r") as fp:
        return json.load(fp)


def load_metadata(metadata_file: Union[Path, str, None]) -> dict:
    """
    Loads metadata from file.
    This can be any arbitrary dictionary and its contents will appear in the
    result archive's metadata.json.
    Useful for keeping track of where each call comes from in a larger
    optimization process.

    Arguments:
      metadata_file: Path to the metadata file
    """
    if not metadata_file:
        return dict()
    if isinstance(metadata_file, dict):
        return metadata_file
    with Path(metadata_file).open("r") as fp:
        meta = json.load(fp)
        if not isinstance(meta, dict):
            raise RuntimeError("Metadata must be JSON serializable dictionary.")
        return meta


def wait_on_result(msg: dramatiq.Message, interval: int = 10, timeout: int = 600) -> object:
    """
    Uses the dramatiq backend mechanism to wait on a result from a worker.

    EXAMPLE ONLY: DO NOT USE IN PRODUCTION

    Arguments:
      msg: The message from the dramatiq send call.
      interval: The time, in seconds, to wait between each check of the backend.
      timeout: The total time, in seconds, to wait for a result before giving up.
    """

    elapsed = 0
    result = None

    # Loop until result found
    while not result:

        # Try to get Result
        try:
            print(f"Checking for result @ {elapsed}s")
            result = msg.get_result(block=False)

        # If no result yet
        except dramatiq.results.ResultMissing as err:

            # Check if we're timed out
            if elapsed >= timeout:
                raise RuntimeError(f"No result found by {elapsed}s")

            # Else wait another interval
            elapsed += interval
            time.sleep(interval)

    return result


def get_result_archive_path(result: object, results_dir: Path) -> Path:
    """
    Get the name of the specific result archive from the backend produced
    result.

    Arguments:
      result: The result object returned by `wait_on_result`
      results_dir: The directory in which all the results will appear.
    """

    raw_path = Path(result["result_archive"])

    return results_dir / raw_path.name


def get_zip_metadata(zip_file: Path) -> Optional[object]:
    """
    Returns the contents of the zip's metadata.json, if it has one.

    Arguments:
      zip_file: The part to the zip we're opening.
    """

    # Open Zip file
    with zipfile.ZipFile(zip_file) as zip:
        meta_file = zipfile.Path(zip) / "metadata.json"

        # Check if `metadata.json` exists
        if not meta_file.exists() and meta_file.is_file():
            print(f"Zip '{str(zip_file)}' has no metadata.json")
            return None

        # If yes, decode its contents
        with meta_file.open("r") as meta:
            return json.load(meta)


def match_msg_to_zip(msg: dramatiq.Message, zip_file: Path) -> bool:
    """
    Checks whether the given message produced the given zip archive.

    Arguments:
      msg: The dramatiq message we're checking against
      zip_file: The path to the zip we're verifying
    """

    msg_id = msg.message_id

    metadata = get_zip_metadata(zip_file)

    return metadata and ("message_info" in metadata) and msg_id == metadata["message_info"]["message_id"]


def watch_results_dir(msg: dramatiq.Message, results_dir: Path, interval: int = 10, timeout: int = 600) -> Path:
    """
    Checks directory every interval to see if any of the zip files match the
    provided message.

    EXAMPLE ONLY: DO NOT USE IN PRODUCTION

    Arguments:
      msg: The message we sent to the broker
      results_dir: dir to look for results archive in
      interval: delay between each check of the results_dir
      timeout: time to search for archive before giving up
    """

    elapsed = 0
    seen = dict()

    # Wait till we're out of time or have a result
    while elapsed <= timeout:
        print(f"Checking for result @ {elapsed}s")
        for zip_file in results_dir.iterdir():

            # Check if file is a valid zip
            valid_zip = zip_file.is_file()
            valid_zip = valid_zip and ".zip" == zip_file.suffix
            valid_zip = valid_zip and zip_file not in seen

            # Skip further checks if not zip
            if not valid_zip:
                continue

            # return file if match found, else mark as seen.
            print(f"Checking zip file: {str(zip_file)}")
            if match_msg_to_zip(msg, zip_file):
                return zip_file
            else:
                seen[zip_file] = True  # Using seen as set

        # Wait for next interval
        elapsed += interval
        time.sleep(interval)

    raise RuntimeError(f"No result found by {elapsed}s")


def polling_results(msg, timeout: int = 800):
    print("Waiting for the results to appear...")
    result_archive = watch_results_dir(msg, results_dir=aws_folder / "results", timeout=timeout)
    result = get_zip_metadata(result_archive)
    print("Result archive found in results dir w/ metadata:")
    print(json.dumps(result, indent="  "))
    print(f"Command completed. Results can be found at:{result_archive}")
    return result_archive


def extract_results(
    result_archive_path: Path, control_opt: bool
) -> tuple[list[float] | None, list[bool] | None, dict | None]:

    print("Extracting results from result zip file...")
    with zipfile.ZipFile(result_archive_path) as result_zip_file:
        # checking the fdm
        fdm_folder = zipfile.Path(result_zip_file) / "Results"

        # Check if `Results` exists
        if not fdm_folder.exists() or not fdm_folder.is_dir():
            print(f"FDM Results folder (Results/) does not exist in the result archive!")
            return None
        # Extracting score from control optimization
        design_score_path = fdm_folder / "control_opt_result.out"
        if design_score_path.exists() and design_score_path.is_file():
            with design_score_path.open("r") as fdm_input_file:
                # TODO: Read the files to get the scores and their corresponding control parameters
                pass
        # Check the Results folder
        folders = [fdm_test for fdm_test in fdm_folder.iterdir()]
        if len(folders) != 4:
            print(f"Not 4 folders in fdm results, meaning that the design is problematic or pipeline had problem.")
            return None, [False], None  # return failure

        extract_folder = fdm_extract_folder
        # print(extract_folder)
        for fdm_test in folders:
            fdm_input = fdm_test / "fdmTB" / "flightDynFast.inp"
            fdm_output = fdm_test / "fdmTB" / "flightDynFastOut.out"
            fdm_input_member = Path("Results", fdm_test.name, "fdmTB", "flightDynFast.inp")
            fdm_output_member = Path("Results", fdm_test.name, "fdmTB", "flightDynFastOut.out")

            if fdm_input.is_file():
                info = result_zip_file.getinfo(str(fdm_input_member))
                info.filename = f"flightDynFast.inp"
                result_zip_file.extract(member=info, path=str(extract_folder))
                with fdm_input.open("r") as fdm_input_file:
                    # TODO: read the fdm input files
                    pass

            # if fdm_output.is_file():
            #     info = result_zip_file.getinfo(str(fdm_output_member))
            #     info.filename = f"flightDynFastOut.out"
            #     result_zip_file.extract(member = info, path = str(extract_folder))
            #     with fdm_output.open("r") as fdm_output_file:
            #         #TODO: read the fdm output files
            #         pass
    if control_opt:
        from sym_cps.optimizers.control_opt.optimizer import ControlOptimizer

        cont_opt = ControlOptimizer(library=None)
        ret = cont_opt.optimize(d_concrete=None)
        best_args = None
        for path_ret in ret["result"]:
            if path_ret["Path"] == 9:
                best_args = path_ret["best_args"]
        return [ret["total_score"]], [True], best_args  # return failure

    # TODO: return the score, corresponding control parameters, and optionally other information from fdm_input/fdm_output if needed.
    return None, [False], None  # return failure
