from sym_cps.grammar import AbstractGrid
from sym_cps.representation.design.abstract import AbstractDesign
from sym_cps.shared.paths import designs_folder
import pickle

from sym_cps.tools.my_io import save_to_file


def remove_edges():
    grid_file = designs_folder / "100__directions_props_grammar_oz2v_w5_p2" / "grid.dat"
    with open(grid_file, "rb") as pickle_file:
        abstract_grid: AbstractGrid = pickle.load(pickle_file)
        abstract_grid.adjacencies = {}
        new_design = AbstractDesign(abstract_grid.name)
        new_design.parse_grid(abstract_grid)
        save_to_file(new_design.plot, absolute_path=designs_folder / "100__directions_props_grammar_oz2v_w5_p2" / "grid_no_edge.pdf")



if __name__ == '__main__':
    remove_edges()