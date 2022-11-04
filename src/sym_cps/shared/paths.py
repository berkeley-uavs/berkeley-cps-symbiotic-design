from __future__ import annotations

import os
from pathlib import Path
from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=['../../../settings.toml'],
)

this_file = Path(os.path.dirname(__file__))
root: Path = this_file.parent.parent.parent

if hasattr(settings, "challenge_data_relative_path"):
    challenge_data = (root / settings.challenge_data_relative_path).resolve()
else:
    challenge_data = (root / "../challenge_data").resolve()

data_folder: Path = challenge_data / "data"
output_folder: Path = challenge_data / "output"
fdm_root_folder: Path = challenge_data / "fdm"

aws_folder: Path = challenge_data / "aws"
designs_folder: Path = output_folder / "designs"
library_folder: Path = output_folder / "library"

fdm_bin_folder: Path = fdm_root_folder / "bin" / "bin" / "bin"
fdm_tmp_folder: Path = fdm_root_folder / "tmp"
fdm_extract_folder: Path = fdm_root_folder / "extract"
prop_table_folder: Path = fdm_root_folder / "Tables"/ "PropData"


component_library_root_path_default: Path = data_folder / "ComponentLibrary" / "results_json"

# Used to set the bounds to parameters that don't have it. Filled by domain expert (looking at the CAD models)
lower_bound_file = component_library_root_path_default.parent / "lower_bounds_chosen.txt"
upper_bound_file = component_library_root_path_default.parent / "upper_bounds_chosen.txt"

design_library_root_path_default: Path = data_folder / "DesignLibrary"

persistence_path: Path = output_folder / "persistence"

reverse_engineering_folder = data_folder / "reverse_engineering"

connectors_components_path = reverse_engineering_folder / "connectors_components_mapping.json"

learned_default_params_path = reverse_engineering_folder / "analysis" / "learned_parameters.json"
