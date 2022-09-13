from __future__ import annotations

import os
from pathlib import Path
from enum import Enum, auto

this_file = Path(os.path.dirname(__file__))
root: Path = this_file.parent.parent.parent

class ExportType(Enum):
    TXT = auto()
    JSON = auto()
    DOT = auto()
    PDF = auto()


data_folder: Path = root / "data"
configuration_files_path: Path = root / "configurations"
output_folder: Path = root / "output"
designs_folder: Path = output_folder / "designs"
library_folder: Path = output_folder / "library"

component_library_root_path_default: Path = (
        data_folder / "ComponentLibrary" / "results_json"
)

# Used to set the bounds to parameters that don't have it. Filled by domain expert (looking at the CAD models)
lower_bound_file = (
        component_library_root_path_default.parent / "lower_bounds_chosen.txt"
)
upper_bound_file = (
        component_library_root_path_default.parent / "upper_bounds_chosen.txt"
)

design_library_root_path_default: Path = data_folder / "DesignLibrary"

persistence_path: Path = output_folder / "persistence"

