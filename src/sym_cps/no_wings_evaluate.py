import pickle

from sym_cps.grammar.rules import AbstractGrid
from sym_cps.representation.design.abstract import AbstractDesign
from sym_cps.representation.design.concrete import DConcrete
from sym_cps.shared.paths import designs_folder

grid_test = 0

designs_numbers = [17]


def get_dconcrete(design_folder_name: str) -> DConcrete:
    file = designs_folder / design_folder_name / "d_concrete.dat"
    with open(file, 'rb') as pickle_file:
        dconcrete: DConcrete = pickle.load(pickle_file)
        return dconcrete


def get_abstract_design(design_folder_name: str) -> AbstractDesign:
    file = designs_folder / design_folder_name / "grid.dat"
    with open(file, 'rb') as pickle_file:
        grid: AbstractGrid = pickle.load(pickle_file)
        new_design = AbstractDesign(design_folder_name)
        new_design.parse_grid(grid)
        return new_design


if __name__ == '__main__':
    for number in designs_numbers:
        folder_name = f"_random_design_{number}"

        """Get directly DConcrete"""
        dconcrete: DConcrete = get_dconcrete(folder_name)

        """Generate DConcrete from AbstractDesign"""
        abstract_design: AbstractDesign = get_abstract_design(folder_name)
        dconcrete: DConcrete = abstract_design.to_concrete()

        """Generate STL and evaluate"""
        dconcrete.choose_default_components_for_empty_ones()
        dconcrete.export_all()
        dconcrete.evaluate()
