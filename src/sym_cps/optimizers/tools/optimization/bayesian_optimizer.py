import math

import numpy as np
import numpy.typing as npt
from scipy.optimize import minimize
from scipy.stats import norm
from sklearn.gaussian_process.kernels import Matern

from sym_cps.optimizers.tools.optimization.bayesian_opt_visualizer import BayesianOptimizationVisualizer
from sym_cps.optimizers.tools.optimization.optimizer_base import OptimizerBase
from sym_cps.optimizers.tools.optimization.problem_base import ProblemBase
from sym_cps.optimizers.tools.optimization.util.surrogate import LogisticClassifier, ScikitGPR, SurrogateInterface


class BayesianOptimizer(OptimizerBase):
    """Optimization usign Bayesian Optimization
    Taking a optimization problem, performs black box optimization which combines a classifier
    Input: problem: A ProblemBase object
    """

    def __init__(self, problem: ProblemBase, debug_level = 1, **kwarg):
        super().__init__(problem=problem)
        self._visualizer = BayesianOptimizationVisualizer()
        self._kernel = Matern(nu=2.5, length_scale=0.05, length_scale_bounds="fixed")
        # self._kernel = Matern(nu=2.5, length_scale=5000, length_scale_bounds = "fixed")
        self._acq_function = self.expected_improvement
        self._surrogate_model_obj: SurrogateInterface = ScikitGPR
        self._surrogate_model_con: SurrogateInterface = LogisticClassifier
        self._xi: float = 0.0
        self._rng = np.random.RandomState(1234)
        self._iteration: int = 1000
        self._num_warn_up_samples: int = 10
        self._explore_num_warm_up: int = 200
        self._explore_num_samples: int = 25
        self._consider_constraint: bool = True
        self._plot_debug: bool = False
        self._plot_freq: int = 10
        self.set_args(**kwarg)

        if self._plot_debug:
            self._visualizer.initialize_design_space(self._problem)

    def set_args(self, **kwarg):
        if "kernel" in kwarg.keys():
            print("Setting Kernel...")
            self._kernel = kwarg["kernel"]
        if "acquisition_function" in kwarg.keys():
            if kwarg["acquisition_function"] == "GP-UCB":
                print("Use GP-UCB as acquisition function")
                self._acq_function = self.upper_confidence_bound
            elif kwarg["acquisition_function"] == "EI":
                print("Use EI as acquisition function")
                self._acq_function = self.expected_improvement
            else:
                s = kwarg["acquisition_function"]
                print(f"Unknown Acquisition function type {s}")
        if "surrogate_model_obj" in kwarg.keys():
            self._surrogate_model_obj = kwarg["surrogate_model_obj"]
        if "surrogate_model_con" in kwarg.keys():
            self._surrogate_model_con = kwarg["surrogate_model_con"]
        if "random_generator" in kwarg.keys():
            self._rng = kwarg["random_generator"]
        if "iteration" in kwarg.keys():
            self._iteration = kwarg["iteration"]
        if "num_warn_up_samples" in kwarg.keys():
            print(f"Set numbers of warm up samples as {self._num_warn_up_samples}")
            self._num_warn_up_samples = kwarg["num_warn_up_samples"]
        if "explore_num_warm_up" in kwarg.keys():
            self._explore_num_warm_up = kwarg["explore_num_warm_up"]
            print(f"Set numbers of exploration warm up samples as {self._explore_num_warm_up}")
        if "explore_num_samples" in kwarg.keys():
            self._explore_num_samples = kwarg["explore_num_samples"]
            print(f"Set numbers of exploration samples as {self._explore_num_samples}")
        if "consider_constraint" in kwarg.keys():
            self._consider_constraint = kwarg["consider_constraint"]
        if "plot_debug" in kwarg.keys():
            self._plot_debug = kwarg["plot_debug"]
        if "plot_freq" in kwarg.keys():
            self._plot_freq = kwarg["plot_freq"]

    def _get_samples(self, n_samples):

        ubound = np.array([u_b for (_, u_b) in self._problem.bounds])
        lbound = np.array([l_b for (l_b, _) in self._problem.bounds])

        return self._rng.uniform(low=lbound, high=ubound, size=(n_samples, self._problem.dim))

    def optimize(self, **kwarg):
        """This function performs maximization!!"""
        if self._plot_debug:
            self._visualizer.plot_objectives()
            self._visualizer.plot_finalize()
            self._visualizer.plot_constraints()
            self._visualizer.plot_finalize()
        self.set_args(**kwarg)

        x_max_valid = None
        y_max_ind_valid = np.full(self._problem.obj_dim, -float("inf"))  # record the best obj value of valid design
        y_max_valid = np.full(self._problem.obj_dim, -float("inf"))  # record the best obj value of valid design

        # seed init
        x_init = np.array(self._problem.opt_array)
        # warnup with random samples
        x_sample = self._get_samples(n_samples=self._num_warn_up_samples)
        # print(x_init, x_sample)
        x_sample = np.concatenate((x_init.reshape(1, -1), x_sample))
        # evaluate the random samples
        for x in x_sample:
            y, v = self._evaluate(parameters=x)
            valid = np.all(v)
            if valid or not self._consider_constraint:
                y_max_ind_valid = np.maximum(y, y_max_ind_valid)
                if self._problem.obj_dominate(y, y_max_valid):
                    # TODO: handle multi-objective parato front
                    y_max_valid = y
                    x_max_valid = x
        # print(self._hist.hist_params)
        # print(self._hist.hist_func)
        # print(self._hist.hist_valid)

        # start performing bayesian optimization
        for i in range(self._iteration):
            self.debug_print(1, "iteration", i)
            obj_model = self._surrogate_model_obj(kernel=self._kernel)
            con_model = self._surrogate_model_con()

            x_explored = self._hist.hist_params
            y_explored = self._hist.hist_func
            v_explored = self._hist.hist_valid

            obj_model.fit(x_explored, y_explored)
            if self._consider_constraint:
                con_model.fit(x_explored, v_explored)

            # apply the surrogate
            x_min = self._explore_with_surrogate(
                obj_model=obj_model, con_model=con_model, y_best=y_max_ind_valid, index=i
            )
            # evaluate the candidate
            y, v = self._evaluate(parameters=x_min)

            valid = np.all(v)
            if valid or not self._consider_constraint:
                y_max_ind_valid = np.maximum(y, y_max_ind_valid)
                if self._problem.obj_dominate(y, y_max_valid):
                    # TODO: handle multi-objective parato front
                    y_max_valid = y
                    x_max_valid = x
            print(f"Iteration {i}: x = {x_min}, y = {y}, y_max = {y_max_valid}")

        return x_max_valid, y_max_valid

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

        return obj_vals, con_vals

    def _explore_with_surrogate(self, obj_model: SurrogateInterface, con_model: SurrogateInterface, y_best, index):
        """leverage the surrogate and optimize the acquicistion function"""
        # find the maximum of the acquisition function
        # find minimum of its negative
        x_min = None
        y_min = float("inf")

        def func(x):
            return -self._acq_function(obj_model=obj_model, con_model=con_model, x=x, y_best=y_best, index=index)

        # func2 = lambda x: -self._acquisition_function_backup(gpr, classifier, x, y_best, xi)
        # generate starting points for global exploration
        warn_samples = self._get_samples(n_samples=self._explore_num_warm_up)
        # print(warn_samples.shape, self._explore_num_warm_up)
        res_array = []
        # warn up
        for x0 in warn_samples:
            test_res = func(x0)
            res_array.append(test_res.item(0))
            if test_res < y_min:
                x_min = x0
                y_min = test_res

        idx_array = np.argsort(res_array).flatten()

        exploring_samples = warn_samples[idx_array[: self._explore_num_samples], :]
        # print(idx_array[:self._explore_num_samples].shape, idx_array.shape, self._explore_num_samples)
        # exploring_samples = self._get_samples(n_samples=self._explore_num_samples)
        # exploring_samples = np.concatenate(warn_samples, exploring_samples)
        self.debug_print(1, "Finding exploration points...")
        for x0 in exploring_samples:
            # print("run", exploring_samples.shape)
            # print("inner", x0, -func(x0), gpr.predict(x0.reshape(1, -1), return_std = True), classifier.predict_proba(x0.reshape(1, -1)))
            res = minimize(func, x0=x0, bounds=self._problem.bounds, method="L-BFGS-B")
            # print("inner", res.success, res.x, res.fun)
            if res.fun < y_min:
                x_min = res.x
                y_min = res.fun

        if self._plot_debug and index % self._plot_freq == 0:
            self._visualizer.plot_acquisition(func, x_min)
            self._visualizer.plot_prediction(obj_model=obj_model, hist=self._hist, x_next=x_min)
            if self._consider_constraint:
                self._visualizer.plot_classification(con_model=con_model, hist=self._hist, x_next=x_min)
            # plot_acquisition(self._X_gold, func, x_min)
            # plot_acquisition(self._X_gold, func2, x_min)

        # print(f"xmax = {x_min} y_max = {-y_min}, y_best = {y_best}")

        # print(x_min, classifier.predict_proba(x_min.reshape(1, -1)))
        return x_min

    def expected_improvement(self, obj_model, con_model, x, y_best, index):
        # print("EI")
        x = x.reshape(1, -1)
        mean, std = obj_model.predict(x)
        # print(mean, std)
        if std == 0.0:
            return 0
        if self._consider_constraint:
            proba = con_model.predict(x)
            # print(proba)
            # proba = classifier.predict_proba(x)

        # compute the expected improvement
        den = mean - y_best - self._xi
        Z = den / std
        ei = den * norm.cdf(Z) + std * norm.pdf(Z)
        # print(proba, classifier.classes_)
        # print("EI:", ei)
        # Consider the probability of invalid inputs
        if self._consider_constraint:
            if proba > 0.2:
                return ei * proba
            else:
                return 0
        else:
            return ei

    def upper_confidence_bound(self, obj_model, con_model, x, y_best, index):
        # print("UCB")
        x = x.reshape(1, -1)
        mean, std = obj_model.predict(x)
        # print(mean, std)
        if std == 0.0:
            return 0
        if self._consider_constraint:
            proba = con_model.predict(x)
            # print(proba)
            # proba = classifier.predict_proba(x)

        # compute the expected improvement
        beta = 2 * math.log((index + 1) ** 2)
        ucb = mean + math.sqrt(beta) * std
        # print(proba, classifier.classes_)
        # print("EI:", ei)
        # Consider the probability of invalid inputs
        if self._consider_constraint:
            if proba > 0.2:
                return ucb * proba
            else:
                return 0
        else:
            return ucb
