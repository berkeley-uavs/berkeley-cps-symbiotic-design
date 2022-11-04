import numpy as np
import numpy.typing as npt
from scipy.optimize import minimize

from sym_cps.optimizers.tools.optimization.optimizer_base import OptimizerBase
from sym_cps.optimizers.tools.optimization.problem_base import ProblemBase


class NMOptimizer(OptimizerBase):
    """Optimization usign Nealson-Mead Local Optimization
    Taking a optimization problem, performs black box optimization which combines a classifier
    Input: problem: A ProblemBase object
    """

    def __init__(self, problem: ProblemBase, **kwarg):
        super().__init__(problem=problem)
        self.set_args(**kwarg)

        self._maxiter = 100000
        self._x0 = self._problem.opt_array

    def set_args(self, **kwarg):
        if "maxiter" in kwarg:
            self._maxiter = kwarg["maxiter"]
        if "x0" in kwarg:
            self._x0 = kwarg["x0"]

    def _get_samples(self, n_samples):

        ubound = np.array([u_b for (_, u_b) in self._problem.bounds])
        lbound = np.array([l_b for (l_b, _) in self._problem.bounds])

        return self._rng.uniform(low=lbound, high=ubound, size=(self._num_warn_up_samples, self._problem.dim))

    def optimize(self, **kwarg):
        # init x list
        self.set_args(**kwarg)

        options = {}
        options["maxiter"] = self._maxiter
        options["disp"] = True
        print(self._evaluate(np.array(self._x0), idx=0))

        ret = minimize(
            lambda x: -self._evaluate(x, idx=0),
            x0=self._x0,
            bounds=self._problem.bounds,
            method="Nelder-Mead",
            options=options,
        )

        print(ret.x, ret.fun)
        return ret.x, ret.fun

    def _evaluate(
        self, parameters: npt.ArrayLike, record: bool = True, idx: int | None = None
    ) -> tuple[list[float], list[bool]]:
        """Evaluates the parameters and returns the objective function value and constraints satisfaction"""
        obj_vals, con_vals = self._problem.evaluate(parameters)
        if idx is not None:
            obj_vals = obj_vals[idx]
            con_vals = con_vals[idx]
        if record:
            self._hist.add_hist(params=parameters, obj_vals=obj_vals, valid=con_vals)

        return obj_vals
