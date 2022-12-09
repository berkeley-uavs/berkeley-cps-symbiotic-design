import pickle

from sym_cps.contract.tester.simplified_selector import SimplifiedSelector
from sym_cps.grammar import AbstractGrid
from sym_cps.representation.design.abstract import AbstractDesign
from sym_cps.representation.design.concrete import DConcrete
from sym_cps.representation.tools.parsers.parse import parse_library_and_seed_designs
from sym_cps.shared.paths import designs_folder

grid_test = 0

designs_numbers = [17]


def get_dconcrete(design_folder_name: str) -> DConcrete:
    file = designs_folder / design_folder_name / "d_concrete.dat"
    with open(file, "rb") as pickle_file:
        dconcrete: DConcrete = pickle.load(pickle_file)
        return dconcrete


def get_abstract_design(design_folder_name: str) -> AbstractDesign:
    print(designs_folder)
    print(design_folder_name)

    file = designs_folder / design_folder_name / "grid.dat"
    print(file)

    with open(file, "rb") as pickle_file:
        grid: AbstractGrid = pickle.load(pickle_file)
        new_design = AbstractDesign(design_folder_name)
        new_design.parse_grid(grid)
        print(new_design.name)
        new_design.save()
        return new_design


def find_components(design: DConcrete):
    selector = SimplifiedSelector()
    c_library, seed_designs = parse_library_and_seed_designs()
    selector.set_library(library=c_library)
    print(type(design))
    print("Helloe")
    print(len(design.components))
    for comp in design.components:
        print(comp.id, comp.library_component.id)
    design.name += "_comp_opt"

    selector.random_local_search(d_concrete=design)


def evaluate_existing_grid(folder_name):
    abstract_design: AbstractDesign = get_abstract_design(folder_name)

    dconcrete: DConcrete = abstract_design.to_concrete()

    dconcrete.choose_default_components_for_empty_ones()

    dconcrete.export_all()

    find_components(dconcrete)

    dconcrete.evaluate()

    dconcrete.export_all()


if __name__ == "__main__":

    for number in designs_numbers:
        # folder_name = f"1__grammar_kep0_w0_p2"
        folder_name = f"2__grammar_yzac_w0_p3"
        # folder_name = f"_random_design_{number}"
        # folder_name = f"_random_design_17"

        # """Get directly DConcrete"""
        # dconcrete: DConcrete = get_dconcrete(folder_name)

        """Generate DConcrete from AbstractDesign"""
        abstract_design: AbstractDesign = get_abstract_design(folder_name)
        dconcrete: DConcrete = abstract_design.to_concrete()

        # """Generate STL and evaluate"""
        # dconcrete.choose_default_components_for_empty_ones()
        #
        # """find component"""
        # find_components(dconcrete)
        #
        # dconcrete.export_all()
        dconcrete.evaluate()
