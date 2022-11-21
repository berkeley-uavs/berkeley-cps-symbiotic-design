from sym_cps.grammar.topology import AbstractTopology
from sym_cps.representation.design.concrete import DConcrete
from sym_cps.shared.designs import designs
from sym_cps.shared.objects import ExportType

designs_to_check = ["TestQuad_Cargo", "NewAxe_Cargo", "PickAxe"]


def assert_topology_from_and_to_json(topology_level: ExportType):
    for design_id in designs_to_check:
        assert_topology_from_and_to_json_design(designs[design_id][0], topology_level)


def assert_topology_from_and_to_json_design(design_original: DConcrete, topology_level: ExportType):

    # Exporting AbstractTopology to file
    topology_json_path_1 = design_original.export(topology_level)

    # Loading AbstractTopology from file
    abstract_topology = AbstractTopology.from_json(topology_json_path_1)

    # Creating DConcrete Object
    design_loaded = DConcrete.from_abstract_topology(abstract_topology)

    assert design_original == design_loaded

    # Exporting AbstractTopology to file
    topology_json_path_2 = design_loaded.export(topology_level)

    # Loading again from file
    abstract_topology_2 = AbstractTopology.from_json(topology_json_path_2)

    # Creating DConcrete Object
    design_loaded_2 = DConcrete.from_abstract_topology(abstract_topology_2)

    assert design_original == design_loaded_2


levels = [ExportType.TOPOLOGY_1, ExportType.TOPOLOGY_2, ExportType.TOPOLOGY_3, ExportType.TOPOLOGY_4]


def test_topology_abstraction_1():
    assert_topology_from_and_to_json(ExportType.TOPOLOGY_1)


def test_topology_abstraction_2():
    assert_topology_from_and_to_json(ExportType.TOPOLOGY_2)


def test_topology_abstraction_3():
    assert_topology_from_and_to_json(ExportType.TOPOLOGY_3)


def test_topology_abstraction_4():
    assert_topology_from_and_to_json(ExportType.TOPOLOGY_4)


test_topology_abstraction_1()
test_topology_abstraction_2()
test_topology_abstraction_3()
test_topology_abstraction_4()
