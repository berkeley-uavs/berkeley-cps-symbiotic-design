# type: ignore
import os
from pathlib import Path

from engineio import json


def save_to_file(
        file_content: str | dict,
        file_name: str,
        folder_name: str | None = None,
        absolute_path: Path | None = None,
) -> Path:
    if Path(file_name).suffix == "":
        file_name += ".txt"

    if absolute_path is not None:
        if absolute_path.suffix == "txt" or absolute_path.suffix == "json":
            file_name = absolute_path.name

    if folder_name is not None and absolute_path is not None:
        raise AttributeError

    from sym_cps.shared.paths import output_folder

    if folder_name is not None:
        file_folder = output_folder / folder_name
    else:
        if absolute_path is not None:
            file_folder = absolute_path
        else:
            file_folder = f"{output_folder}"

    if not os.path.exists(file_folder):
        os.makedirs(file_folder)

    file_path: Path = Path(file_folder) / file_name

    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))

    _write_file(file_content, file_path)

    print(f"File saved in {str(file_path)}")
    return file_path


def _write_file(file_content: str | dict, absolute_path: Path):
    if isinstance(file_content, dict):
        file_content = json.dumps(file_content, indent=4)
        if Path(absolute_path).suffix != ".json":
            absolute_path_str = str(absolute_path) + ".json"
            absolute_path = Path(absolute_path_str)
        with open(absolute_path, "w") as f:
            json.dump(json.loads(file_content), f, indent=4, sort_keys=True)
        f.close()
    else:
        with open(absolute_path, "w") as f:
            f.write(file_content)
        f.close()
