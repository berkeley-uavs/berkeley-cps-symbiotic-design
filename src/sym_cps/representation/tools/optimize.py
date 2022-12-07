from sym_cps.contract.tester.simplified_selector import SimplifiedSelector
from sym_cps.representation.design.concrete import DConcrete
from sym_cps.shared.library import c_library


def find_components(design: DConcrete):
    selector = SimplifiedSelector()
    selector.set_library(library=c_library)
    print(type(design))
    print("Helloe")
    print(len(design.components))
    for comp in design.components:
        print(comp.id, comp.library_component.id)
    design.name += "_comp_opt"

    selector.random_local_search(d_concrete=design)


def set_direction(design: DConcrete):
    # TODO Pier
    # find the propeller pair based on symmetry
    # assign the propeller in the same pair with different direction/proptype
    # if the propeller is facing up: one with 1/1 another with -1/-1
    # if the propeller is facing down: one with -1/1 another with direction 1/-1
    pass
