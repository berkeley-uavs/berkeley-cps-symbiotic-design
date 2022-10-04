from enum import Enum, auto
import numpy.typing as npt
import numpy as np

from sym_cps.representation.design.concrete import DConcrete
from sym_cps.representation.design.concrete.elements.parameter import Parameter
from sym_cps.representation.design.concrete.elements.design_parameters import DesignParameter
from sym_cps.evaluation import evaluate_design
from sym_cps.shared.paths import designs_folder, ExportType
from sym_cps.optimizers.tools.optimization.problem_base import ProblemBase


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
        self._params, self._init_params_val_array = self._vectorize_d_concrete(d_concrete=self._d_concrete)
        # set the attribute from the ProblemBase
        self._bounds = self._get_bounds(self._params)
        self._opt_array = np.array(self._init_params_val_array)
        self.set_obj_dim(4) # 4 objective : four tests supported
        self.set_con_dim(1) # 1 constraint: the design is valid (can have FDM output) or not 

    def set_parameters(self, parameters: npt.ArrayLike) -> None:
        """Set the d concrete using the param_val as the value for each design parameter"""
        if len(self._params) != parameters.shape[0]:
            print(f"Mismatched parameter size: {len(self._params)} and {parameters.shape}")
            raise Exception()
        for param, val in zip(self._params, parameters):
            param.value = val

    def evaluate(self, parameters: npt.ArrayLike):
        # set the parameters
        self.set_parameters(parameters)
        # export to design_swri
        self._d_concrete.export(ExportType.JSON) 
        # call the pipeline for evaluation
        design_json_path = designs_folder / self._d_concrete.name /"design_swri.json"

        ret = evaluate_design(design_json_path=design_json_path,
                        metadata={"extra_info": "full evaluation example"},
                        timeout=800)
        return ret
        



    def _vectorize_d_concrete(self, d_concrete: DConcrete)-> tuple[list[Parameter | DesignParameter], list[float]]:
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

            #debug 
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
                    if min_val is None:
                        min_val = param.min
                    if max_val is None:
                        max_val = param.max

                    if min_val > param.min:
                        min_val = param.min
                    if max_val < param.max:
                        max_val = param.max
                except: # not specified value in corpus
                    min_val = -10000
                    max_val = 10000
            bounds.append((min_val, max_val))
        return bounds