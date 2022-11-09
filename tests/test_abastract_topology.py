import json
from sym_cps.grammar.tools import main

from sym_cps.grammar.topology import AbstractTopology
from sym_cps.representation.design.concrete import DConcrete
from sym_cps.shared.designs import designs
from sym_cps.shared.objects import ExportType


def assert_topology_from_and_to_json(topology_level: ExportType):
    """Test of AbstractTopology at the level of abstraction 1 (lowest)"""
    # Loading DConcrete Object
    test_quad_original = designs["TestQuad"][0]

    # Exporting AbstractTopology to file
    topology_json_path_1 = test_quad_original.export(topology_level)

    # Loading AbstractTopology from file
    abstract_topology = AbstractTopology.from_json(topology_json_path_1)

    # Creating DConcrete Object
    test_quad_loaded = DConcrete.from_abstract_topology(abstract_topology)

    if not test_quad_original == test_quad_loaded:
        print("not euqal")

    # Exporting AbstractTopology to file
    topology_json_path_2 = test_quad_loaded.export(topology_level)

    # Loading again from file
    abstract_topology_2 = AbstractTopology.from_json(topology_json_path_2)

    # Creating DConcrete Object
    test_quad_loaded_2 = DConcrete.from_abstract_topology(abstract_topology)

    assert test_quad_original == test_quad_loaded_2


levels = [ExportType.TOPOLOGY_1, ExportType.TOPOLOGY_2, ExportType.TOPOLOGY_3, ExportType.TOPOLOGY_4]


def test_topology_abstraction_1():
    assert_topology_from_and_to_json(ExportType.TOPOLOGY_1)

#
# def test_topology_abstraction_2():
#     assert_topology_from_and_to_json(ExportType.TOPOLOGY_2)
#
#
# def test_topology_abstraction_3():
#     assert_topology_from_and_to_json(ExportType.TOPOLOGY_3)
#
#
# def test_topology_abstraction_4():
#     assert_topology_from_and_to_json(ExportType.TOPOLOGY_4)


#
# test_topology_abstraction_1()
# test_topology_abstraction_2()
# test_topology_abstraction_3()
# test_topology_abstraction_4()
