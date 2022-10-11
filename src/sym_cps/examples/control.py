from sym_cps.optimizers.control_opt.optimizer import ControlOptimizer
from sym_cps.optimizers.concrete_opt import ConcreteOptimizer, ConcreteStrategy
from sym_cps.optimizers.params_opt import ParametersOptimizer, ParametersStrategy, ParametersConstraint
from sym_cps.optimizers.topo_opt import TopologyOptimizer, TopologyStrategy
from sym_cps.representation.design.concrete import DConcrete
from sym_cps.representation.design.topology import DTopology
from sym_cps.representation.tools.parsers.parse import parse_library_and_seed_designs
from sym_cps.representation.tools.parsers.parsing_designs import parse_design_from_design_swri
from sym_cps.shared.paths import output_folder, ExportType

"""Loading Library and Seed Designs"""
c_library, designs = parse_library_and_seed_designs()

"""Loading optimizers at different abstraction layers"""
topo_opt = TopologyOptimizer(library=c_library)
concr_opt = ConcreteOptimizer(library=c_library)
para_opt = ParametersOptimizer(library=c_library)
cont_opt = ControlOptimizer(library=c_library)


def control_opt(design_name: str = "TestQuad", designs_dat_file: str = "designs.dat"):

    """Get a design concrete"""
    design_concrete: DConcrete = designs[design_name][0]

    """Call the optimizer"""
    result: DConcrete = cont_opt.optimize(
        d_concrete=design_concrete
    )

if __name__ == '__main__':
    control_opt()