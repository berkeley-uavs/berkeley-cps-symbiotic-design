from sym_cps.cli import _parse_design
from sym_cps.grammar import AbstractGrid
from sym_cps.representation.design.abstract import AbstractDesign
import pickle

from sym_cps.shared.paths import data_folder

grid_test = 1

grid_file = data_folder / "custom_designs" / f"grid/test_{grid_test}/grid.dat"

with open(grid_file, "rb") as pickle_file:
    abstract_grid: AbstractGrid = pickle.load(pickle_file)
    new_design = AbstractDesign(abstract_grid.name)
    new_design.parse_grid(abstract_grid)
    new_design.plot.show()