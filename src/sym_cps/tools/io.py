# type: ignore
import os
from pathlib import Path

from sym_cps.shared.paths import output_folder


def save_to_file(
    file_content: str,
    file_name: str,
    folder_name: str | None = None,
    absolute_folder_path: Path | None = None,
) -> Path:
    if Path(file_name).suffix == "":
        file_name += ".txt"

    if folder_name is not None and absolute_folder_path is not None:
        raise AttributeError

    if folder_name is not None:
        file_folder = output_folder / folder_name

    elif absolute_folder_path is not None:
        file_folder = f"{absolute_folder_path}"

    else:
        file_folder = f"{output_folder}"

    if not os.path.exists(file_folder):
        os.makedirs(file_folder)

    file_path: Path = Path(file_folder) / file_name

    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))

    with open(file_path, "w") as f:  # mypy crashes on this line, i don't know why
        f.write(file_content)

    f.close()

    print(f"File saved in {str(file_path)}")
    return file_path
