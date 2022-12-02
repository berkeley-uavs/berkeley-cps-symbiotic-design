import pickle

from dill import load
from sym_cps.cli import _parse_design
from sym_cps.representation.design.concrete import DConcrete
from sym_cps.shared.paths import output_folder, designs_folder

grid_test = 0

designs_numbers = [45]

if __name__ == '__main__':
    for number in designs_numbers:
        file = designs_folder / f"_random_design_{number}" / "d_concrete.dat"
        with open(file, 'rb') as pickle_file:
            dconcrete: DConcrete = pickle.load(pickle_file)
            dconcrete.choose_default_components_for_empty_ones()
            dconcrete.export_all()
            dconcrete.evaluate()
