from abc import ABC, abstractmethod
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import PolynomialFeatures

class SurrogateInterface(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def fit(self, X, Y):
        """Built the surrogate model"""

    @abstractmethod
    def predict(self, x):
        """Access the model"""

class ScikitGPR(SurrogateInterface):
    def __init__(self, kernel, n_restarts_optimizer = 5, alpha = 0.0001, random_state = None):
        self._kernel = kernel
        self._random_state = random_state
        self._n_restarts_optimizer = 5
        self._alpha = 0.0001
        self._gpr = GaussianProcessRegressor(kernel=kernel, 
                                             random_state = self._random_state, 
                                             normalize_y = True,
                                             optimizer = "fmin_l_bfgs_b",
                                             n_restarts_optimizer = self._n_restarts_optimizer,
                                             alpha = self._alpha)

    def fit(self, X, Y) -> None:
       self._gpr.fit(X, Y)

    def predict(self, x) -> tuple[float, float]:
        return self._gpr.predict(x, return_std=True)

class LogisticClassifier(SurrogateInterface):
    def __init__(self, preprocessor = None):
        if preprocessor is None:
            preprocessor = PolynomialFeatures(3, include_bias=True)

        self._preprocessor = preprocessor
        self._classifier = LogisticRegression(max_iter=1000, warm_start=True)
    
    def fit(self, X, Y):
        self._classifier.fit(self._preprocessor.fit_transform(X), Y.reshape(-1,))

    def predict(self, x) -> float:
        return self._classifier.predict_proba(self._preprocessor.fit_transform(x))[:, 1]