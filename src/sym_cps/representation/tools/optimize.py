import json

from sym_cps.contract.tester.simplified_selector import SimplifiedSelector
from sym_cps.representation.design.concrete import DConcrete
from sym_cps.shared.library import c_library
from sym_cps.shared.paths import best_component_choices_path
from sym_cps.tools.my_io import save_to_file


def find_components(design: DConcrete):
    design.name += "_comp_opt"
    selector = SimplifiedSelector()
    selector.set_library(library=c_library)
    print(type(design))
    print("Helloe")
    print(len(design.components))
    for comp in design.components:
        print(comp.id, comp.library_component.id)
    if best_component_choices_path.is_file():
        best_component_choices = json.load(open(best_component_choices_path))
    else:
        best_component_choices: dict[int, dict[str]] = {}
    n = design.n_propellers
    if n in best_component_choices.keys():
        best_motor, best_batt, best_prop = best_component_choices[n]
        new_components = {}
        if "Motor" in best_component_choices[n].keys():
            new_components["Motor"] = best_motor
        if "Battery" in best_component_choices[n].keys():
            new_components["Battery"] = best_batt
        if "Propeller" in best_component_choices[n].keys():
            new_components["Propeller"] = best_prop
        design.replace_all_components(new_components)
        return
    best_motor, best_batt, best_prop = selector.random_local_search(d_concrete=design)
    print(f"N={n}")
    print(f"BEST-Motor={best_motor}")
    print(f"BEST-Battery={best_batt}")
    print(f"BEST-Propeller={best_prop}")
    best_component_choices[n] = {}
    if best_motor is not None:
        best_component_choices[n]["Motor"] = best_motor
    if best_batt is not None:
        best_component_choices[n]["Battery"] = best_batt
    if best_prop is not None:
        best_component_choices[n]["Propeller"] = best_prop
    save_to_file(best_component_choices, absolute_path=best_component_choices_path)


def set_direction(design: DConcrete):
    # TODO Pier
    # find the propeller pair based on symmetry
    # assign the propeller in the same pair with different direction/proptype
    # if the propeller is facing up: one with 1/1 another with -1/-1
    # if the propeller is facing down: one with -1/1 another with direction 1/-1
    pass
