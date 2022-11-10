from __future__ import annotations

import json
from enum import Enum, auto

from sym_cps.optimizers import Optimizer
from sym_cps.shared.library import c_library
from sym_cps.shared.paths import connectors_components_path, learned_default_params_path, reverse_engineering_folder


class ExportType(Enum):
    TXT = auto()
    JSON = auto()
    SUMMARY = auto()
    DOT = auto()
    PDF = auto()
    EVALUATION = auto()
    TOPOLOGY_1 = auto()
    TOPOLOGY_2 = auto()
    TOPOLOGY_3 = auto()
    TOPOLOGY_4 = auto()


def export_type_to_topology_level(export_type: ExportType) -> int:
    return int(export_type.name.split("_")[1])


connections_map: dict = json.load(open(connectors_components_path))
structures: dict = json.load(open(reverse_engineering_folder / "analysis" / "structure.json"))
default_parameters: dict = json.load(open(learned_default_params_path))


optimizer: Optimizer = Optimizer(c_library)
