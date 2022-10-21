from __future__ import annotations

import os
from pathlib import Path

this_file = Path(os.path.dirname(__file__))
root: Path = this_file.parent.parent.parent

data_folder: Path = root / "data"
configuration_files_path: Path = root / "configurations"
output_folder: Path = root / "output"
aws_folder: Path = output_folder / "aws"
designs_folder: Path = output_folder / "designs"
library_folder: Path = output_folder / "library"
fdm_root_folder: Path = root / "fdm"
fdm_bin_folder: Path = root / "fdm" / "bin" / "bin" / "bin"
fdm_tmp_folder: Path = root / "fdm" / "tmp"
fdm_extract_folder: Path = root / "fdm" / "extract"

component_library_root_path_default: Path = data_folder / "ComponentLibrary" / "results_json"

# Used to set the bounds to parameters that don't have it. Filled by domain expert (looking at the CAD models)
lower_bound_file = component_library_root_path_default.parent / "lower_bounds_chosen.txt"
upper_bound_file = component_library_root_path_default.parent / "upper_bounds_chosen.txt"

design_library_root_path_default: Path = data_folder / "DesignLibrary"

persistence_path: Path = output_folder / "persistence"

reverse_engineering_folder = data_folder / "reverse_engineering"

connectors_components_path = reverse_engineering_folder / "connectors_components_mapping.json"

learned_default_params_path = reverse_engineering_folder / "analysis" / "learned_parameters.json"
