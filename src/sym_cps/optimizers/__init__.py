from dataclasses import dataclass
from enum import Enum, auto

from sym_cps.representation.library import Library

class OptimizationStrategy(Enum):
    random_strategy = auto()

@dataclass(frozen=True)
class Optimizer:
    library: Library


