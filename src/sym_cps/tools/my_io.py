# type: ignore
import json
import os
import pickle
from pathlib import Path
from typing import OrderedDict

from matplotlib.figure import Figure

from sym_cps.tools.strings import sort_dictionary


def save_to_file(
    file_content: str | dict | Figure | object,
    file_name: str | None = None,
    folder_name: str | None = None,
    absolute_path: Path | None = None,
) -> Path:

    from sym_cps.shared.paths import output_folder

    if folder_name is not None:
        file_folder = output_folder / folder_name
    elif absolute_path is not None:
        if absolute_path.suffix == "":
            file_folder = absolute_path
        else:
            file_folder = absolute_path.parent
            file_name = absolute_path.name
    else:
        file_folder = f"{output_folder}"

    if Path(file_name).suffix == "" and isinstance(file_content, dict):
        file_name += ".json"
    elif Path(file_name).suffix == "" and isinstance(file_content, Figure):
        file_name += ".pdf"
    elif Path(file_name).suffix == "" and isinstance(file_content, str):
        file_name += ".txt"
    elif Path(file_name).suffix == "":
        file_name += ".dat"

    if folder_name is not None and absolute_path is not None:
        raise AttributeError

    if not os.path.exists(file_folder):
        os.makedirs(file_folder)

    file_path: Path = Path(file_folder) / file_name

    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))

    _write_file(file_content, file_path)

    print(f"{file_name} saved in {str(file_path)}")
    return file_path


def _write_file(file_content: str | dict | Figure | object, absolute_path: Path):
    if absolute_path.is_file():
        print(f"File already exists: {absolute_path}")
        name = absolute_path.name
        suffix = absolute_path.suffix
        index = name.split("_ver_")
        if len(index) > 1:
            new_name = f"{name}_ver_{int(index[1]) + 1}" + suffix
        else:
            new_name = f"{name}_ver_1" + suffix
        absolute_path = absolute_path.parent / new_name
        print(f"New file name: {absolute_path}")
    if isinstance(file_content, OrderedDict):
        with open(absolute_path, "w") as f:
            file_content = json.dumps(file_content, indent=4)
            json.dump(json.loads(file_content), f, indent=4, sort_keys=False)
        f.close()
    elif isinstance(file_content, dict):
        # file_content_origin = file_content
        file_content = sort_dictionary(file_content)
        file_content = json.dumps(file_content, indent=4)
        if Path(absolute_path).suffix != ".json":
            absolute_path_str = str(absolute_path) + ".json"
            absolute_path = Path(absolute_path_str)
        with open(absolute_path, "w") as f:
            json.dump(json.loads(file_content), f, indent=4)
        f.close()
    elif isinstance(file_content, Figure):
        file_content.savefig(absolute_path)
    elif isinstance(file_content, str):
        with open(absolute_path, "w") as f:
            f.write(file_content)
        f.close()
    else:
        with open(absolute_path, "wb") as f:
            try:
                pickle.dump(obj=file_content, file=f)
            except Exception as e:
                raise e
        f.close()
