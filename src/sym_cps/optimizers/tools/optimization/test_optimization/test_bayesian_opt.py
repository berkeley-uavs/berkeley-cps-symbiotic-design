from sym_cps.optimizers.tools.optimization.problem_base import ProblemBase
from sym_cps.optimizers.tools.optimization.bayesian_optimizer import BayesianOptimizer
import numpy.typing as npt
import numpy as np


class TestProblem(ProblemBase):

    def __init__(self, bounds, opt_array, obj_dim, con_dim, obj_func, con_func):
        self._bounds: list[tuple[float, float]] = bounds
        self._opt_array: npt.ArrayLike = opt_array
        self._obj_dim = obj_dim
        self._con_dim = con_dim

        self._obj_func = obj_func
        self._con_func = con_func

    def obj_dominate(self, obj1: npt.ArrayLike, obj2: npt.ArrayLike):
        return obj1[0] > obj2[0]

    def evaluate(self, parameters: npt.ArrayLike):
        """return the objective function or invalid parameters"""
        return self._obj_func(parameters), self._con_func(parameters)

    def set_parameters(self, parameters: npt.ArrayLike) -> None:
        pass


def drop_wave_equation_1d(x):
    """
    1 dimensional simplification of drop wave equation from https://www.sfu.ca/~ssurjano/drop.html
    The drop wave equation has multiple local minima
    """
    return -(1 + np.cos(12*np.sqrt(x**2)))/((0.5 * x**2) + 2)

def cos_constraint(x):
    return np.cos(5*x) < -0.3

def test_bayes_opt():
    bounds = [(-5, 5)]
    opt_array = np.array([1])
    obj_dim = 1
    con_dim = 1
    problem = TestProblem(bounds=bounds, 
                          opt_array=opt_array,
                          obj_dim=obj_dim,
                          con_dim=con_dim,
                          obj_func=drop_wave_equation_1d,
                          con_func=cos_constraint)

    kwarg = {}
    kwarg["plot_debug"] = True
    kwarg["plot_freq"] = 100
    kwarg["consider_constraint"] = False
    kwarg["acquisition_function"] = "GP-UCB"

    optimizer = BayesianOptimizer(problem=problem, **kwarg)
    x_max_valid, y_max_valid = optimizer.optimize()
    print(x_max_valid, y_max_valid)


if __name__ == "__main__":
    test_bayes_opt()