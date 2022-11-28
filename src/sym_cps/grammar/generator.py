from sym_cps.grammar.rules import generate_random_topology, get_seed_design_topo
from sym_cps.representation.design.abstract import AbstractDesign


def design_test_quad():
    new_design = AbstractDesign(f"TestQuad_Cargo_test")
    new_design.parse_grid(get_seed_design_topo("TestQuad_Cargo"))
    new_design.save()
    d_concrete = new_design.to_concrete()
    d_concrete.export_all()


def random_designs_n(n: int = 100):
    for i in range(0, n):
        new_design = AbstractDesign(f"_random_design_{i}")
        new_design.parse_grid(generate_random_topology())
        new_design.save(folder_name=f"designs/{new_design.name}")
        d_concrete = new_design.to_concrete()
        d_concrete.export_all()
        # d_concrete.evaluate()


if __name__ == "__main__":
    random_designs_n(1)
    # design_test_quad()
