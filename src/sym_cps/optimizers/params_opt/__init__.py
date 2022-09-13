from enum import Enum, auto

from sym_cps.optimizers import Optimizer


class ParametersStrategy(Enum):
    random_strategy = auto()


class ParametersOptimizer(Optimizer):
    pass
