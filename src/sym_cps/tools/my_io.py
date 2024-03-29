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
        sort: bool = True,
        overwrite: bool = False,
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

    _write_file(file_content, file_path, sort=sort, overwrite=overwrite)

    print(f"{file_name} saved in {str(file_path)}")
    return file_path


def rename_if_already_exists(absolute_path: Path):
    if "design_swri" in str(absolute_path):
        return absolute_path
    new_path = absolute_path
    if absolute_path.is_file():
        print(f"File already exists: {absolute_path}")
        version = 1
        suffix = absolute_path.suffix
        for file in absolute_path.parent.iterdir():
            if absolute_path.stem in file.stem:
                index = file.stem.split("_ver_")
                if len(index) > 1:
                    if int(index[1]) > version:
                        version = int(index[1])
        new_name = f"{absolute_path.stem}_ver_{version + 1}" + suffix
        new_path = absolute_path.parent / new_name
        print(f"New file name: {new_path}")
    if absolute_path.is_dir():
        print(f"'Directory already exists: {absolute_path}")
        name = absolute_path.stem
        index = name.split("_ver_")
        if len(index) > 1:
            new_name = f"{name}_ver_{int(index[1]) + 1}"
        else:
            new_name = f"{name}_ver_1"
        new_path = absolute_path.parent / new_name
        print(f"New dir name: {new_path}")
    return new_path


def _write_file(file_content: str | dict | Figure | object, absolute_path: Path, sort: bool = True,
                overwrite: bool = False):
    if not overwrite:
        absolute_path = rename_if_already_exists(absolute_path)
    if isinstance(file_content, OrderedDict):
        with open(absolute_path, "w") as f:
            file_content = json.dumps(file_content, indent=4)
            json.dump(json.loads(file_content), f, indent=4, sort_keys=False)
        f.close()
    elif isinstance(file_content, dict):
        # file_content_origin = file_content
        if sort:
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
