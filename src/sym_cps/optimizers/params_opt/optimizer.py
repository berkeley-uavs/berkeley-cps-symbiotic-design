from sym_cps.optimizers import Optimizer
from sym_cps.optimizers.tools.optimization.bayesian_optimizer import BayesianOptimizer
from sym_cps.representation.design.concrete import DConcrete
from sym_cps.representation.design.concrete.elements.parameter import Parameter
from sym_cps.representation.design.concrete.elements.design_parameters import DesignParameter
from sym_cps.optimizers.params_opt.param_opt_problem import ParameterOptimizationProblem, ParametersStrategy, ParametersConstraint


class ParametersOptimizer(Optimizer):

    def _vectorize(self,         
        d_concrete: DConcrete,
        strategy: ParametersStrategy,
        constraints: ParametersConstraint
    ) -> tuple[list[Parameter | DesignParameter], list[float]]:
        """
        Create twos array to help vectorize the parameters and facilitate mapping back the values to the design
        The first element in the tuple is the list of parameter object that can be set by calling .value
        The second element in the tuple is the array of the parameter values for optimization
        """
        if strategy == ParametersStrategy.bayesian_strategy:
            # create vector for optimization
            if constraints == ParametersConstraint.design_parameter:
                params = list(d_concrete.design_parameters.values())
                param_val_array = [param.value for param in params]
            elif constraints == ParametersConstraint.component_parameter:
                params = []
                for component in d_concrete.components:
                    params.extend(component.parameters.values())
                param_val_array = [param.value for param in params]

            #debug 
            # for param, val in zip(params, param_val_array):
            #     print(param.id, val)
        return params, param_val_array


    def _get_bounds(self,         
        d_params: list[DesignParameter]
    ) -> list[tuple[float, float]]:
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

        

    def optimize(self, 
        d_concrete: DConcrete,
        strategy: ParametersStrategy,
        constraints: ParametersConstraint
    ) -> DConcrete:
        problem = ParameterOptimizationProblem(d_concrete=d_concrete, strategy=strategy, constraint=constraints)

        #debug 
        for param, val in zip(problem._params, problem._init_params_val_array):
            print(param.id, val)
        print(problem._bounds)
        if strategy == ParametersStrategy.bayesian_strategy:
            print("Optimizing Parameters using Bayesian Optimization!")
            optimizer = BayesianOptimizer(problem)
            