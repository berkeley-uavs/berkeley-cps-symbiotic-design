"""
optimizer_base.py
Define the class OptimizerBase as an abstract class for optimizer.
"""
from abc import ABC, abstractmethod

import numpy.typing as npt

from sym_cps.optimizers.tools.optimization.problem_base import ProblemBase
from sym_cps.optimizers.tools.optimization.util.exceptions import (  # pylint: disable=import-error, no-name-in-module
    InValidDesignException,
)
from sym_cps.optimizers.tools.optimization.util.history import (  # pylint: disable=import-error, no-name-in-module
    History,
)


class OptimizerBase(ABC):
    """
    Define the base class for all optimizer, either a self-implemented optimzer or an interface
    to other optimization library
    """

    def __init__(self, problem: ProblemBase, debug_level=1):
        # debug_level 1: print every detail during each iteration
        # debug_level 2: print every steps in the algorithm
        self._problem: ProblemBase = problem
        self._debug_level: int = debug_level
        self._fail_value: float = float("inf")
        self._hist: History = History()
        self.reset_history()

    @abstractmethod
    def set_args(self, **kwarg):
        """Set the arguments before calling optimize"""

    @abstractmethod
    def optimize(self, **kwarg):
        """
        Abstract method that optimizes a design problem
        Implementation
        """

    def reset_history(self):
        """Clear all history"""
        x_dim = self._problem.dim
        self._hist.reset_history(x_dim, self._problem.obj_dim, self._problem.con_dim)

    @property
    def hist(self) -> History:
        return self._hist

    def debug_print(self, level_constraint: int, *args, **kwargs):
        if self._debug_level > level_constraint:
            print(*args, **kwargs)

    @abstractmethod
    def _evaluate(
        self, parameters: npt.ArrayLike, record: bool = True, idx: int | None = None
    ) -> tuple[list[float], list[bool]]:
        """Evaluates the parameters and returns the objective function value and constraints satisfaction"""
        obj_vals, con_vals = self._problem.evaluete(parameters)
        if record:
            self._hist.add_hist(params=parameters, obj_vals=obj_vals, valid=con_vals)
        return obj_vals, con_vals

    def _update_parameters(self, parameters: npt.ArrayLike) -> None:
        self._problem.set_parameters(parameters=parameters)
