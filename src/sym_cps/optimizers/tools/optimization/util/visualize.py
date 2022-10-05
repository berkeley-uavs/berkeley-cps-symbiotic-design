"""
visualize.py
Define the class ContinuousDesignProblemVisualizer for visualing the continous optimization problem
"""
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import numpy.typing as npt
from sym_cps.optimizers.tools.optimization.optimizer_base import OptimizerBase  # pylint: disable=import-error, no-name-in-module
from sym_cps.optimizers.tools.optimization.problem_base import ProblemBase # pylint: disable=import-error, no-name-in-module

class ContinuousProblemVisualizer(object):
    """Used for visualizing the design problem and design space"""
    def __init__(self, resolution: int = 100):
        self._problem = None
        self._res = resolution
        self._x = None
        self._y = None
        self._xv = None
        self._yv = None
        self._f_gold = None
        self._x_valid = None
        self._dim = None

    @property
    def res(self) -> int:
        return self._res

    @res.setter
    def res(self, res):
        self._res = res


    def initialize_design_space(self, problem: ProblemBase):
        """Plot the design space (Only apply to 1d or 2d design space)"""
        self._problem = problem
        
        lbound = [l_b for (l_b, _) in problem.bounds]
        ubound = [u_b for (_, u_b) in problem.bounds]
        if self._problem.dim == 1:
            self._dim = 1
            self._x = np.linspace(lbound[0], ubound[0], self.res)
            self._f_gold = self._get_F_1d(self._x) # function value
            self._x_valid = self._get_valid_1d(self._x)
        elif self._problem.dim == 2:
            self._dim = 2
            self._x = np.linspace(lbound[0], ubound[0], self.res)
            self._y = np.linspace(lbound[1], ubound[1], self.res)
            self._xv, self._yv = np.meshgrid(self._x, self._y)
            self._f_gold = self._get_F_2d(self._xv, self._yv) # function value
            self._x_valid = self._get_valid_2d(self._xv, self._yv)
        else:
            raise Exception("Not supported for high dimension")


    def _get_F_1d(self, x_array: npt.ArrayLike):
        """Get all objectives in the design space"""
        problem_dim = self._problem.obj_dim
        f_shape = (*(x_array.shape), problem_dim) 
        # adding dimensions, each element becomes multiple objectives
        f_array = np.zeros(f_shape)
        for i, _x in enumerate(x_array):
            obj_vals, con_vals = self._problem.evaluate(np.array([_x]))
            f_array[i] = obj_vals.flatten()
        return f_array
    
    def _get_F_2d(self, xv_array: npt.ArrayLike, yv_array: npt.ArrayLike):
        problem_dim = self._problem.obj_dim
        f_shape = (*(xv_array.shape), problem_dim) 
        # adding dimensions, each element becomes multiple objectives
        f_array = np.zeros(f_shape)
        for i in range(xv_array.shape[0]):
            for j in range(xv_array.shape[1]):
                obj_vals, con_vals = self._problem.evaluate(np.array([xv_array[i, j], yv_array[i, j]]))
                f_array[i, j] = obj_vals.flatten()
        return f_array

    def _get_valid_1d(self, x_array: npt.ArrayLike):
        """Get all constraints in the design space"""
        constraint_dim = self._problem.con_dim
        x_valid_shape = (*(x_array.shape), constraint_dim) # adding dimensions, each element becomes multiple objectives
        x_valid = np.zeros(x_valid_shape)
        for i, _x in enumerate(x_array):
            obj_vals, con_vals = self._problem.evaluate(np.array([_x]))
            x_valid[i] = con_vals.flatten()
        return x_valid

    def _get_valid_2d(self, xv_array: npt.ArrayLike, yv_array: npt.ArrayLike):
        constraint_dim = self._problem.con_dim
        x_valid_shape = (*(xv_array.shape), constraint_dim) 
        # adding dimensions, each element becomes multiple objectives
        x_valid_array = np.zeros(x_valid_shape)
        for i in range(xv_array.shape[0]):
            for j in range(xv_array.shape[1]):
                obj_vals, con_vals = self._problem.evaluate(np.array([xv_array[i, j], yv_array[i, j]]))
                x_valid_array[i, j] = con_vals.flatten()
        return x_valid_array
        

    def plot_objectives(self, show: bool = False, idx: int = None):
        if self._dim == 1:
            self._plot_objectives_1d(idx=idx)
        elif self._dim == 2:
            self._plot_objectives_2d(idx=idx)
        else:
            raise Exception(f"Dimension ({self._dim}) not supported!")
        
        if show:
            self.plot_finalize()

    def plot_constraints(self, show: bool = False, idx: int = None):
        if self._dim == 1:
            self._plot_constraints_1d(idx=idx)
        elif self._dim == 2:
            self._plot_constraints_2d(idx=idx)
        else:
            raise Exception(f"Dimension ({self._dim}) not supported!")
        
        if show:
            self.plot_finalize()

    def plot_optimizer_hist_params_1d(self, optimizer: OptimizerBase):
        """Plot the searched point of 1d"""
        hist = optimizer.hist
        p_hist = hist.hist_params
        f_hist = hist.hist_func
        
        plt.scatter(p_hist, f_hist, color=cm.Greys(np.linspace(0, 1, hist.length)), marker='x')
        plt.legend()

    def plot_optimizer_hist_params_2d(self, optimizer: OptimizerBase):
        """Plot the searched point of 2d"""
        hist = optimizer.hist
        p_hist = hist.hist_params

        plt.scatter(p_hist[:, 0], p_hist[:, 1], color=cm.Greys(np.linspace(0, 1, hist.length)), marker = "x")
        #plt.legend()


    def plot_best_params_1d(self, best_param, best_f):
        plt.scatter(best_param, best_f, c = "cyan", marker="*", label="Best")
        plt.legend()

    def plot_best_params_2d(self, best_param):
        plt.scatter(best_param[0], best_param[1], c = "cyan", marker="*", label="Best")
        plt.legend()


    def plot_optimizer_convergence(self, optimizer: OptimizerBase):
        f_hist = optimizer.hist.hist_func
        v_hist = optimizer.hist.hist_valid

        f_best = float("inf")
        f_best_hist = np.zeros(f_hist.shape)
        for i, f in enumerate(f_hist):
            if f < f_best and v_hist[i]:
                f_best = f
            f_best_hist[i] = f_best
        plt.plot(np.arange(1, f_hist.shape[0]+1), f_best_hist.flatten() - f_best, label="convergence")
        plt.yscale("log")
        plt.legend()
        plt.title("Convergence")
        plt.show()

    # def plot_history_1d(self, hist_x: npt.ArrayLike, hist_f: npt.ArrayLike):
    #     """Plot the 1d history provided in the space"""
    #     plt.plot(hist_x, hist_f, color=cm.Greys(np.linspace(0, 1, hist_x.shape[0])), marker='x', mew=3, label='samples')

    # def plot_history_2d(self, hist_x: npt.ArrayLike):
    #     """Plot the 2d history provided in the space"""
    #     plt.scatter(hist_x[:, 0], hist_x[:, 1], color=cm.Greys(np.linspace(0, 1, hist_x.shape[0])), marker = "x")

    # def plot_best_point_1d(self, best_pos: npt.ArrayLike, best_val: float):
    #     """Plot the optimal point finded in the space"""
    #     plt.scatter(best_pos, best_val, c = "cyan", marker="*")

    # def plot_best_point_2d(self, best_pos: npt.ArrayLike):
    #     """Plot the optimal point finded in the space"""
    #     plt.scatter(best_pos[0], best_pos[1], c = "cyan", marker="*")

    def plot_finalize(self):
        plt.show()

    def _plot_objectives_1d(self, idx: int = None):
        if idx is None:
            for idx in range(self._f_gold.shape[-1]):
                plt.plot(self._x, self._f_gold[:, idx], 'y--', lw=1, label=f'objective {idx}')
        else: 
            plt.plot(self._x, self._f_gold[:, idx], 'y--', lw=1, label=f'objective {idx}')
        plt.legend()

    def _plot_objectives_2d(self, idx: int = None):
        if idx is None:
            for idx in range(self._f_gold.shape[-1]):        
                c = plt.pcolormesh(self._xv, self._yv, self._f_gold[1:, 1:, idx], cmap = 'coolwarm', shading='flat', label=f'objective {idx}')
                plt.colorbar(c)
        else: 
            c = plt.pcolormesh(self._xv, self._yv, self._f_gold[1:, 1:, idx], cmap = 'coolwarm', shading='flat', label=f'objective {idx}')
            plt.colorbar(c)

    def _plot_constraints_1d(self, idx: int = None):
        if idx is None:
            for idx in range(self._x_valid.shape[-1]):
                plt.plot(self._x, self._x_valid[:, idx], 'y--', lw=1, label=f'constraint {idx}')
        else: 
            plt.plot(self._x, self._x_valid[:, idx], 'y--', lw=1, label=f'constraint {idx}')  
        plt.legend()      

    def _plot_constraints_2d(self, idx: int = None):
        if idx is None:
            for idx in range(self._x_valid.shape[-1]):        
                c = plt.pcolormesh(self._xv, self._yv, self._x_valid[1:, 1:, idx], cmap = 'coolwarm', shading='flat', label=f'constraint {idx}')
                plt.colorbar(c)
        else: 
            c = plt.pcolormesh(self._xv, self._yv, self._x_valid[1:, 1:, idx], cmap = 'coolwarm', shading='flat', label=f'constraint {idx}')
            plt.colorbar(c)