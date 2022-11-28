from sym_cps.cli import _parse_design

grid_test = 0

if __name__ == '__main__':
    dconcrete = _parse_design([f"--grid=grid/test_{grid_test}/grid.dat"])
    dconcrete.export_all()
    dconcrete.evaluate()
