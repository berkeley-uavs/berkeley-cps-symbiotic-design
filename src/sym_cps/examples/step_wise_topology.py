from sym_cps.examples.library import parse_library, export_library
from sym_cps.representation.design.concrete import DConcrete, Component, Connection
from sym_cps.representation.design.tools import generate_designs_info_files
from sym_cps.representation.design.topology import DTopology
from sym_cps.representation.library import Library
from sym_cps.representation.tools.parsers.parse import parse_library_and_seed_designs
from sym_cps.tools.persistance import load

"""Loading Library and Seed Designs"""

# To update the .dat files and the exports run:
# parse_library()
# export_library()

designs: dict[str, tuple[DConcrete, DTopology]] = load("designs.dat")
c_library: Library = load("library.dat")

generate_designs_info_files(designs, "TestQuad")

# test_quad_design = designs["TestQuad"][0]
#
# ret = test_quad_design.evaluate()
# print(ret)


def design_test_quad():
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

