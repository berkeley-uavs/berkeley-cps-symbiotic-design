from sym_cps.optimizers.concrete_opt import ConcreteOptimizer, ConcreteStrategy
from sym_cps.optimizers.params_opt import ParametersOptimizer
from sym_cps.optimizers.topo_opt import TopologyOptimizer, TopologyStrategy
from sym_cps.representation.design.concrete import DConcrete, Component, Connection
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


def random_topology(design_name: str = "Trowel", designs_dat_file: str = "designs.dat"):


    d_concrete = DConcrete(name="test")

    fuselage = c_library.components["capsule_fuselage"]
    hub = c_library.components["0394od_para_hub_4"]

    # First add a fuselage
    fuselage_instance = Component(id="fuse", library_component=fuselage)
    hub_fuselage = Component(id="hub_1", library_component=hub)

    connector_a, connector_b = c_library.get_connectors(fuselage_instance.c_type, hub_fuselage.c_type, "BOTTOM")

    connection = Connection(
        component_a=fuselage_instance,
        connector_a=connector_a,
        component_b=hub_fuselage,
        connector_b=connector_b,
    )

    d_concrete.add_node(fuselage_instance)
    d_concrete.add_node(hub_fuselage)

    d_concrete.connect(connection)


if __name__ == '__main__':
    random_topology()
