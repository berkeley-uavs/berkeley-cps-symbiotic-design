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

from sym_cps.evaluation.fdm_ret import FDMResult
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
    try:
        with zipfile.ZipFile(zip_file) as zip:
            meta_file = zipfile.Path(zip) / "metadata.json"

            # Check if `metadata.json` exists
            if not meta_file.exists() and meta_file.is_file():
                print(f"Zip '{str(zip_file)}' has no metadata.json")
                return None

            # If yes, decode its contents
            with meta_file.open("r") as meta:
                return json.load(meta)
    except zipfile.BadZipFile as e:
        print(e)


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
    result_archive = watch_results_dir(msg, results_dir=aws_folder / "d2c_results", timeout=timeout)
    result = get_zip_metadata(result_archive)
    print("Result archive found in results dir w/ metadata:")
    # print(json.dumps(result, indent="  "))
    print(f"Command completed. Results can be found at:{result_archive}")
    return result_archive


def extract_results(result_archive_path: Path, control_opt: bool) -> dict:

    print("Extracting results from result zip file...")
    fdm_extract_info = {}  # the object for collecting the score and stl files
    fdm_extract_info["status"] = "FAIL"

    with zipfile.ZipFile(result_archive_path) as result_zip_file:
        # checking the fdm
        fdm_folder = zipfile.Path(result_zip_file) / "Results"

        # Check if `Results` exists
        if not fdm_folder.exists() or not fdm_folder.is_dir():
            print(f"FDM Results folder (Results/) does not exist in the result archive!")
            return fdm_extract_info
        # Check the Results folder
        folders = [fdm_test for fdm_test in fdm_folder.iterdir()]

        extract_folder = fdm_extract_folder
        # extract stl file
        stl_folder = zipfile.Path(result_zip_file) / "workingdir"
        stl_file = stl_folder / "uav_gen.stl"
        stl_member = Path("workingdir", "uav_gen.stl")

        if stl_file.is_file():
            info = result_zip_file.getinfo(str(stl_member))
            info.filename = f"uav_gen.stl"
            result_zip_file.extract(member=info, path=str(extract_folder))

        fdm_extract_info["stl_file_path"] = str(extract_folder / info.filename)
        output_file_names = []
        for fdm_test in folders:
            fdm_input = fdm_test / "fdmTB" / "flightDynFast.inp"
            fdm_output = fdm_test / "fdmTB" / "flightDynFastOut.out"
            fdm_input_member = Path("Results", fdm_test.name, "fdmTB", "flightDynFast.inp")
            fdm_output_member = Path("Results", fdm_test.name, "fdmTB", "flightDynFastOut.out")

            if fdm_input.is_file():
                info = result_zip_file.getinfo(str(fdm_input_member))
                info.filename = f"{fdm_test.name}_flightDynFast.inp"
                result_zip_file.extract(member=info, path=str(extract_folder))
                with fdm_input.open("r") as fdm_input_file:

                    # TODO: read the fdm input files
                    pass

            if fdm_output.is_file():
                info = result_zip_file.getinfo(str(fdm_output_member))
                info.filename = f"{fdm_test.name}_flightDynFastOut.out"
                result_zip_file.extract(member=info, path=str(extract_folder))
                output_file_names.append((fdm_test.name, info.filename))

        for fdm_test_name, file_name in output_file_names:
            fdm_ret_path = extract_folder / file_name
            ret = FDMResult(file_path=fdm_ret_path)
            try:
                score = ret.get_metrics("Path_traverse_score_based_on_requirements")
            except:
                score = None
            fdm_extract_info[fdm_test_name] = score
        fdm_extract_info["status"] = "SUCCESS"
    if control_opt:
        from sym_cps.optimizers.control_opt.optimizer import ControlOptimizer

        cont_opt = ControlOptimizer(library=None)
        ret = cont_opt.optimize(d_concrete=None)
        best_args = None
        for path_ret in ret["result"]:
            if path_ret["Path"] == 9:
                best_args = path_ret["best_args"]
        fdm_extract_info["total_score"] = ret["total_score"]
        fdm_extract_info["best_args"] = best_args

    # TODO: return the score, corresponding control parameters, and optionally other information from fdm_input/fdm_output if needed.
    return fdm_extract_info
