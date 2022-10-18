from enum import Enum, auto

import numpy as np
import numpy.typing as npt

from sym_cps.optimizers.tools.optimization.problem_base import ProblemBase
from sym_cps.representation.design.concrete import DConcrete
from sym_cps.representation.design.concrete.elements.design_parameters import DesignParameter
from sym_cps.representation.design.concrete.elements.parameter import Parameter
from sym_cps.shared.paths import ExportType, designs_folder


class ParametersStrategy(Enum):
    random_strategy = auto()
    bayesian_strategy = auto()


class ParametersConstraint(Enum):
    design_parameter = auto()
    component_parameter = auto()


class ParameterOptimizationProblem(ProblemBase):
    """Defines the optimization problem for parameter optimization
    All parameter optimization strategy receives the problem as input.
    """

    def __init__(self, d_concrete: DConcrete, strategy: ParametersStrategy, constraint: ParametersConstraint):
        super().__init__()
        self._d_concrete = d_concrete
        self._strategyType = strategy
        self._constraintType = constraint

        self._bounds = None
        self._params = None
        self._init_params = None

        # get bounds, parameters
        self._params, self._opt_array = self._vectorize_d_concrete(d_concrete=self._d_concrete)
        # set the attribute from the ProblemBase
        self._bounds = self._get_bounds(self._params)
        self.set_obj_dim(1)  # 4 objective : four tests supported
        self.set_con_dim(1)  # 1 constraint: the design is valid (can have FDM output) or not

    def set_parameters(self, parameters: npt.ArrayLike) -> None:
        """Set the d concrete using the param_val as the value for each design parameter"""
        if len(self._params) != parameters.shape[0]:
            print(f"Mismatched parameter size: {len(self._params)} and {parameters.shape}")
            raise Exception()
        for param, val in zip(self._params, parameters):
            param.value = val

    def evaluate(self, parameters: npt.ArrayLike) -> tuple[list[float], list[bool]]:
        # set the parameters
        self.set_parameters(parameters)
        # export to design_swri
        self._d_concrete.export(ExportType.JSON)
        # call the pipeline for evaluation
        design_json_path = designs_folder / self._d_concrete.name / "design_swri.json"

        # obj_vals, con_vals = evaluate_design(
        #     design_json_path=design_json_path,
        #     metadata={"extra_info": "full evaluation example"},
        #     timeout=800,
        #     control_opt=True
        # )

        obj_vals = np.array([-np.sum(parameters**2)])
        con_vals = np.array([parameters[0] > parameters[1] and parameters[1] ** 2 - parameters[2] > 1])
        print("Warning, it is still not connected to evaluation pipeline!!!")
        # TODO: Return obj_vals and con_vals

        return obj_vals, con_vals

    def obj_dominate(self, obj1: npt.ArrayLike, obj2: npt.ArrayLike):
        """Compare multi-objective"""
        return obj1[0] > obj2[0]

    def _vectorize_d_concrete(self, d_concrete: DConcrete) -> tuple[list[Parameter | DesignParameter], list[float]]:
        """
        Create two arrays to help vectorize the parameters and facilitate mapping back the values to the design
        The first element in the tuple is the list of parameter object that can be set by calling .value
        The second element in the tuple is the array of the parameter values for optimization
        """
        # create vector for optimization
        if self._constraintType == ParametersConstraint.design_parameter:
            params = list(d_concrete.design_parameters.values())
            param_val_array = [param.value for param in params]
        elif self._constraintType == ParametersConstraint.component_parameter:
            params = []
            for component in d_concrete.components:
                params.extend(component.parameters.values())
            param_val_array = [param.value for param in params]

            # debug
            # for param, val in zip(params, param_val_array):
            #     print(param.id, val)
        return params, param_val_array

    def _get_bounds(self, d_params: list[DesignParameter]) -> list[tuple[float, float]]:
        bounds = []
        for d_param in d_params:
            min_val = None
            max_val = None
            for param in d_param.parameters:
                try:
                    param_min = param.min
                except:
                    param_min = None

                try:
                    param_max = param.max
                except:
                    param_max = None

                if min_val is None:
                    min_val = param_min
                elif param_min is None:
                    pass
                elif min_val > param_min:
                    min_val = param.min

                if max_val is None:
                    max_val = param_max
                elif param_max is None:
                    pass
                elif max_val < param_max:
                    max_val = param_max

            if min_val is None:
                min_val = -10000
            if max_val is None:
                max_val = 10000

            bounds.append((min_val, max_val))
        return bounds
