from sym_cps.cli import _parse_design

grid_test = 1

if __name__ == "__main__":
    dconcrete = _parse_design([f"--grid=grid/test_{grid_test}/grid.dat"])
    dconcrete.choose_default_components_for_empty_ones()
    dconcrete.export_all()
    dconcrete.evaluate()
