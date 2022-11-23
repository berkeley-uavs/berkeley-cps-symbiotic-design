from sym_cps.representation.design.abstract.abstract_design import AbstractDesign
from sym_cps.grammar.rules import generate_random_topology, get_seed_design_topo
from sym_cps.grammar.topology import AbstractTopology
from sym_cps.representation.design.concrete import DConcrete
from sym_cps.shared.paths import designs_folder
from sym_cps.representation.design.concrete import DConcrete
from sym_cps.shared.objects import ExportType


def design_test_quad():
    test_quad_at = AbstractTopology.from_json(designs_folder / "TestQuad_Cargo" / "topology_summary_4.json")
    new_design = AbstractDesign(f"TestQuad_Cargo")
    # new_design.parse_grid(generate_random_topology())
    new_design.parse_grid(get_seed_design_topo("TestQuad_Cargo"))
    new_design.save()
    abstract_topology = AbstractTopology.from_abstract_design(new_design)

    return abstract_topology


def random_designs_to_d_concrete():
    new_design = AbstractDesign(f"random_design_test")
    new_design.parse_grid(generate_random_topology())
    new_design.save(folder_name=f"designs/generated/{new_design.name}")
    abstract_topology = AbstractTopology.from_abstract_design(new_design)
    d_concrete = DConcrete.from_abstract_topology(abstract_topology)
    d_concrete.export_all()


def random_designs_to_d_concrete_n(n: int = 100):
    for i in range(0, n):
        new_design = AbstractDesign(f"random_design_{i}")
        new_design.parse_grid(generate_random_topology())
        new_design.save(folder_name=f"designs/{new_design.name}")
        d_concrete = DConcrete.from_abstract_design(new_design)
        d_concrete.export_all()
        d_concrete.evaluate()


def random_designs():
    for i in range(0, 100):
        new_design = AbstractDesign(f"random_{i}")
        new_design.parse_grid(generate_random_topology())
        new_design.save()


def abstract_topo_from_random():
    # res = []
    for i in range(0, 100):
        new_design = AbstractDesign(f"random_{i}")
        new_design.parse_grid(generate_random_topology())
        new_design.save()
        design_loaded = DConcrete.from_abstract_design(new_design)
        design_loaded.export(ExportType.TOPOLOGY_1)
        # res.append(abstract_topology)
    # return res


if __name__ == "__main__":
    random_designs_to_d_concrete_n(1)
