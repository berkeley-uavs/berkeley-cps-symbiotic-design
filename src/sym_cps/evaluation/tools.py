"""
File adapted from:
https://github.com/LOGiCS-Project/swri-simple-uam-example
"""

import json
import time
import zipfile
from pathlib import Path

import dramatiq
from simple_uam import direct2cad
from simple_uam.worker import has_backend
from typing import Optional, Union

from sym_cps.shared.paths import output_folder


def load_design(design_file: Path) -> object:
    """
    Loads a design from file.

    Arguments:
      design_file: Path to the design file
    """
    with Path(design_file).open('r') as fp:
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
    with Path(metadata_file).open('r') as fp:
        meta = json.load(fp)
        if not isinstance(meta, dict):
            raise RuntimeError("Metadata must be JSON serializable dictionary.")
        return meta


def wait_on_result(
        msg: dramatiq.Message,
        interval: int = 10,
        timeout: int = 600) -> object:
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


def get_result_archive_path(
        result: object,
        results_dir: Path) -> Path:
    """
    Get the name of the specific result archive from the backend produced
    result.

    Arguments:
      result: The result object returned by `wait_on_result`
      results_dir: The directory in which all the results will appear.
    """

    raw_path = Path(result['result_archive'])

    return results_dir / raw_path.name


def get_zip_metadata(
        zip_file: Path) -> Optional[object]:
    """
    Returns the contents of the zip's metadata.json, if it has one.

    Arguments:
      zip_file: The part to the zip we're opening.
    """

    # Open Zip file
    with zipfile.ZipFile(zip_file) as zip:
        meta_file = zipfile.Path(zip) / 'metadata.json'

        # Check if `metadata.json` exists
        if not meta_file.exists() and meta_file.is_file():
            print(f"Zip '{str(zip_file)}' has no metadata.json")
            return None

        # If yes, decode its contents
        with meta_file.open('r') as meta:
            return json.load(meta)


def match_msg_to_zip(
        msg: dramatiq.Message,
        zip_file: Path) -> bool:
    """
    Checks whether the given message produced the given zip archive.

    Arguments:
      msg: The dramatiq message we're checking against
      zip_file: The path to the zip we're verifying
    """

    msg_id = msg.message_id

    metadata = get_zip_metadata(zip_file)

    return metadata and ('message_info' in metadata) and msg_id == metadata['message_info']['message_id']


def watch_results_dir(
        msg: dramatiq.Message,
        results_dir: Path,
        interval: int = 10,
        timeout: int = 600) -> Path:
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
            valid_zip = valid_zip and '.zip' == zip_file.suffix
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


def polling_results(msg):
    print("Waiting for the results to appear...")
    result_archive = watch_results_dir(
        msg,
        results_dir=output_folder,
        timeout=600
    )
    result = get_zip_metadata(result_archive)
    print("Result archive found in results dir w/ metadata:")
    print(json.dumps(result, indent="  "))
    print(f"Command completed. Results can be found at:{result_archive}")
    return result_archive



if __name__ == '__main__':
    main()
