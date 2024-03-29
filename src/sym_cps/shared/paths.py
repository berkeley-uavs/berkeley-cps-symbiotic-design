from __future__ import annotations

import os
from pathlib import Path

from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=["../../../settings.toml"],
)

this_file = Path(os.path.dirname(__file__))
repo_folder: Path = this_file.parent.parent.parent

if hasattr(settings, "challenge_data_relative_path"):
    challenge_data = (repo_folder / settings.challenge_data_relative_path).resolve()
else:
    challenge_data = (repo_folder / "../challenge_data").resolve()

data_folder: Path = challenge_data / "data"
output_folder: Path = challenge_data / "output"
fdm_root_folder: Path = challenge_data / "fdm"

aws_folder: Path = challenge_data / "aws"
designs_folder: Path = output_folder / "designs"
library_folder: Path = output_folder / "library"

fdm_bin_folder: Path = fdm_root_folder / "bin" / "bin" / "bin"
fdm_tmp_folder: Path = fdm_root_folder / "tmp"
fdm_extract_folder: Path = fdm_root_folder / "extract"
prop_table_folder: Path = fdm_root_folder / "Tables" / "PropData"

component_library_root_path_default: Path = data_folder / "ComponentLibrary" / "results_json"
default_study_params_path = data_folder / "default_study_params" / "study_params.csv"

# Used to set the bounds to parameters that don't have it. Filled by domain expert (looking at the CAD models)
lower_bound_file = component_library_root_path_default.parent / "lower_bounds_chosen.txt"
upper_bound_file = component_library_root_path_default.parent / "upper_bounds_chosen.txt"

design_library_root_path_default: Path = data_folder / "DesignLibrary"

persistence_path: Path = output_folder / "persistence"

reverse_engineering_folder = data_folder / "reverse_engineering"

connectors_components_path = reverse_engineering_folder / "connectors_components_backup.json"
manual_connectors_components_path = reverse_engineering_folder / "manual_connections_learned.json"

grammar_rules_path = reverse_engineering_folder / "grammar_rules.json"
grammar_rules_path_new = reverse_engineering_folder / "grammar_rules_new.json"
grammar_rules_processed_path = reverse_engineering_folder / "grammar_rules_processed.json"
grammar_statistics = reverse_engineering_folder / "grammar_statistics.txt"

stats_folder = output_folder / "stats"
designs_generated_stats_path = lambda tag: stats_folder / f"{tag}_random_designs_stats.json"
random_topologies_generated_path = lambda tag: stats_folder / f"{tag}_random_topologies_generated.json"
random_topologies_all_path = output_folder / f"random_topologies_generated.json"
stats_file_path = output_folder / "stats.json"
stats_file_txt_path = output_folder / "stats.txt"
stats_speeds_file_path = output_folder / "stats_speeds.json"

structures_path = reverse_engineering_folder / "analysis" / "structure.json"
best_component_choices_path = output_folder / "reverse_engineering" / "best_component_choices.json"
manual_default_parameters_path = output_folder / "reverse_engineering" / "shared_parameters_manual.json"
learned_default_params_path = output_folder / "reverse_engineering" / "shared_parameters.json"
component_selection_path = output_folder / "reverse_engineering" / "component_choice.json"

summary_structure_path = output_folder / "analysis" / "isomorphisms" / "structure_summary.json"
isomorphisms_data_path = output_folder / "analysis" / "isomorphisms" / "isomorphisms_data.json"

popular_nodes_keys_path = output_folder / "analysis" / "popular_node_keys.json"
