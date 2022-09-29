from enum import Enum, auto

from sym_cps.optimizers import Optimizer
from sym_cps.optimizers.tools.bayesian_opt import BayesianOptimizer
from sym_cps.representation.design.concrete import DConcrete
from sym_cps.representation.design.concrete.elements.parameter import Parameter
from sym_cps.representation.design.concrete.elements.design_parameters import DesignParameter


class ParametersStrategy(Enum):
    random_strategy = auto()
    bayesian_strategy = auto()

class ParameterConstraint(Enum):
    design_parameter = auto()
    component_parameter = auto()

class ParametersOptimizer(Optimizer):

    def _vectorize(self,         
        d_concrete: DConcrete,
        strategy: ParametersStrategy,
        constraints: ParameterConstraint
    ) -> tuple[list[Parameter | DesignParameter], list[float]]:
        """
        Create twos array to help vectorize the parameters and facilitate mapping back the values to the design
        The first element in the tuple is the list of parameter object that can be set by calling .value
        The second element in the tuple is the array of the parameter values for optimization
        """
        if strategy == ParametersStrategy.bayesian_strategy:
            # create vector for optimization
            if constraints == ParameterConstraint.design_parameter:
                params = list(d_concrete.design_parameters.values())
                param_val_array = [param.value for param in params]
            elif constraints == ParameterConstraint.component_parameter:
                params = []
                for component in d_concrete.components:
                    params.extend(component.parameters.values())
                param_val_array = [param.value for param in params]

            #debug 
            for param, val in zip(params, param_val_array):
                print(param.id, val)
        return params, param_val_array

    def optimize(self, 
        d_concrete: DConcrete,
        strategy: ParametersStrategy,
        constraints: ParameterConstraint
    ) -> DConcrete:

        params, param_val_array = self._vectorize(d_concrete=d_concrete, strategy=strategy, constraints=constraints)
        if strategy == ParametersStrategy.bayesian_strategy:
            print("Optimizing Parameters using Bayesian Optimization!")
            optimizer = BayesianOptimizer()
