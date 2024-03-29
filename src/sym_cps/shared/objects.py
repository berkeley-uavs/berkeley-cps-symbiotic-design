from __future__ import annotations

from enum import Enum, auto

from sym_cps.optimizers import Optimizer
from sym_cps.shared.library import c_library


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
    DAT = auto()


def export_type_to_topology_level(export_type: ExportType) -> int:
    return int(export_type.name.split("_")[1])


optimizer: Optimizer = Optimizer(c_library)
