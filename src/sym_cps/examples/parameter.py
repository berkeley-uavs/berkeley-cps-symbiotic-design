from sym_cps.optimizers.concrete_opt import ConcreteOptimizer
from sym_cps.optimizers.params_opt import ParametersConstraint, ParametersOptimizer, ParametersStrategy
from sym_cps.optimizers.topo_opt import TopologyOptimizer
from sym_cps.representation.design.concrete import DConcrete
from sym_cps.representation.tools.parsers.parse import parse_library_and_seed_designs

"""Loading Library and Seed Designs"""
c_library, designs = parse_library_and_seed_designs()

"""Loading optimizers at different abstraction layers"""
topo_opt = TopologyOptimizer(library=c_library)
concr_opt = ConcreteOptimizer(library=c_library)
para_opt = ParametersOptimizer(library=c_library)


def parameter_opt(design_name: str = "TestQuad", designs_dat_file: str = "designs.dat"):

    """Get a design concrete"""
    design_concrete: DConcrete = designs[design_name][0]

    """Call the optimizer"""
    result: DConcrete = para_opt.optimize(
        d_concrete=design_concrete,
        strategy=ParametersStrategy.bayesian_strategy,
        constraints=ParametersConstraint.design_parameter,
    )


if __name__ == "__main__":
    parameter_opt()
