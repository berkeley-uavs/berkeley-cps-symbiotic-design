from ast import Call
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import numpy.typing as npt
from typing import Callable
from sym_cps.optimizers.tools.optimization.util.visualize import ContinuousProblemVisualizer
from sym_cps.optimizers.tools.optimization.util.history import History
from sym_cps.optimizers.tools.optimization.util.surrogate import SurrogateInterface

class BayesianOptimizationVisualizer(ContinuousProblemVisualizer):
    def __init__(self, resolution: int = 100):
        super().__init__(resolution=resolution)


    def plot_acquisition(self, acq: Callable[[npt.ArrayLike], float], x_next: npt.ArrayLike):
        if self._problem.dim == 1:
            X = self._x
            Y = np.zeros(X.shape)
            for i, x in enumerate(X):
                Y[i] = acq(x)
            plt.plot(X, Y, 'r-', lw=1, label='Acquisition function')
            plt.axvline(x=x_next, ls='--', c='k', lw=1,
                        label='Next sampling location')
            plt.legend()
            plt.show()
        elif self._problem.dim == 2:
            X = self._xv
            Y = self._yv

            F = np.zeros(X.shape)
            for i in range(X.shape[0]):
                for j in range(X.shape[1]):
                    F[i, j] = acq(np.array([X[i, j], Y[i, j]]))
            c = plt.pcolormesh(X, Y, F, cmap='coolwarm', shading='nearest')
            plt.colorbar(c)
            plt.scatter(x_next[0], x_next[1], c="cyan", marker="*")
            plt.legend()
            plt.title("Acquisition function")
            plt.show()


    def plot_classification(self, con_model: SurrogateInterface, hist: History, x_next=None):
        x_explored = hist.hist_params
        x_explored_valid = hist.hist_valid
        if self._problem.dim == 1:
            X = self._x
            X_valid = self._x_valid
            prob = con_model.predict(X.reshape(-1, 1))
            plt.plot(X, prob, 'r-', lw=1, label='probability of classfication')
            #plt.plot(X, Y, 'y--', lw=1, label='objective')
            plt.plot(X, X_valid, 'b-', lw=1, label='classification')
            plt.scatter(x_explored, 
                     x_explored_valid, 
                    #  color=cm.Greys(np.linspace(0, 1, x_explored.shape[0])), 
                     marker='x', 
                    #  mew=3, 
                     label='samples')
            if x_next is not None:
                plt.axvline(x=x_next, ls='--', c='k', lw=1)
            plt.legend()
            plt.show()
        elif self._problem.dim == 2:
            X = self._xv
            Y = self._yv
            F_gold = self._f_gold
            Valid_gold = self._x_valid

            Prob = np.zeros(X.shape)
            for i in range(X.shape[0]):
                for j in range(X.shape[1]):
                    Prob[i, j] = con_model.predict(np.array([[X[i, j], Y[i, j]]]))

            c = plt.pcolormesh(X, Y, Prob, cmap='coolwarm', shading='nearest')
            plt.colorbar(c)
            plt.scatter(x_explored[:, 0], x_explored[:, 1], color=cm.Greys(
                np.linspace(0, 1, x_explored.shape[0])), marker="x")
            if x_next is not None:
                plt.scatter(x_next[0], x_next[1], c="cyan", marker="*")
            plt.legend()
            plt.title("Classification")
            plt.show()

            c = plt.pcolormesh(
                X, Y, Valid_gold, cmap='coolwarm', shading='nearest')
            plt.colorbar(c)
            plt.scatter(x_explored[:, 0], x_explored[:, 1], color=cm.Greys(
                np.linspace(0, 1, x_explored.shape[0])), marker="x")
            if x_next is not None:
                plt.scatter(x_next[0], x_next[1], c="cyan", marker="*")
            plt.legend()
            plt.title("True Classification")
            plt.show()

            result = (Prob > 0.5).astype("int")
            result = 2*result - 1
            error = result - Valid_gold
            c = plt.pcolormesh(X, Y, error, cmap='coolwarm', shading='nearest')
            plt.colorbar(c)
            plt.scatter(x_explored[:, 0], x_explored[:, 1], color=cm.Greys(
                np.linspace(0, 1, x_explored.shape[0])), marker="x")
            if x_next is not None:
                plt.scatter(x_next[0], x_next[1], c="cyan", marker="*")
            plt.legend()
            plt.title("Classification Errors")
            plt.show()

    def plot_prediction(self, obj_model:SurrogateInterface, hist: History, x_next=None):
        x_explored = hist.hist_params
        y_explored = hist.hist_func
        if self._problem.dim == 1:
            X = self._x
            Y = self._f_gold
            mean, std = obj_model.predict(X.reshape(-1, 1))
            plt.fill_between(X.ravel(),
                            mean.ravel() + 2 * std,
                            mean.ravel() - 2 * std,
                            alpha=0.1)
            plt.plot(X, Y, 'y--', lw=1, label='objective')
            plt.plot(X, mean, 'b-', lw=1, label='Surrogate function')
            plt.scatter(x_explored, 
                     y_explored, 
                    #  color=cm.Greys(np.linspace(0, 1, x_explored.shape[0])), 
                     marker='x', 
                    #  mew=3, 
                     label='explored samples')
            if x_next is not None:
                plt.axvline(x=x_next, ls='--', c='k', lw=1)
            plt.legend()
            plt.show()

        elif self._problem.dim == 2:
            X = self._xv
            Y = self._yv
            F_gold = self._f_gold

            Mean = np.zeros(X.shape)
            Std = np.zeros(X.shape)
            for i in range(X.shape[0]):
                for j in range(X.shape[1]):
                    Mean[i, j], Std[i, j] = obj_model.predict(np.array([[X[i, j], Y[i, j]]]))
            # print(X)
            c = plt.pcolormesh(X, Y, (Mean - F_gold),
                            cmap='coolwarm', shading='nearest')
            plt.colorbar(c)
            plt.scatter(x_explored[:, 0], 
                        x_explored[:, 1], 
                        color=cm.Greys(np.linspace(0, 1, x_explored.shape[0])), 
                        marker="x")
            # print(X_next)
            if x_next is not None:
                plt.scatter(x_next[0], x_next[1], c="cyan", marker="*")
            plt.legend()
            plt.title("error to gold")
            plt.show()

            c = plt.pcolormesh(X, Y, Mean, cmap='coolwarm', shading='nearest')
            plt.colorbar(c)
            plt.scatter(x_explored[:, 0], 
                        x_explored[:, 1], 
                        color=cm.Greys(np.linspace(0, 1, x_explored.shape[0])), 
                        marker="x")
            # print(X_next)
            if x_next is not None:
                plt.scatter(x_next[0], x_next[1], c="cyan", marker="*")
            plt.legend()
            plt.title("Prediction")
            plt.show()

            c = plt.pcolormesh(X, Y, F_gold, cmap='coolwarm', shading='nearest')
            plt.colorbar(c)
            plt.scatter(x_explored[:, 0], 
                        x_explored[:, 1], 
                        color=cm.Greys(np.linspace(0, 1, x_explored.shape[0])), 
                        marker="x")
            # print(X_next)
            if x_next is not None:
                plt.scatter(x_next[0], x_next[1], c="cyan", marker="*")
            plt.legend()
            plt.title("Gold")
            plt.show()

            c = plt.pcolormesh(X, Y, Std, cmap='coolwarm', shading='nearest')
            plt.colorbar(c)
            plt.scatter(x_explored[:, 0], 
                        x_explored[:, 1], 
                        color=cm.Greys(np.linspace(0, 1, x_explored.shape[0])), 
                        marker="x")
            print(x_next)
            if x_next is not None:
                plt.scatter(x_next[0], x_next[1], c="cyan", marker="*")
            plt.legend()
            plt.title("Standard Deviation")
            plt.show()