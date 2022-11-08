# from sym_cps.representation.tools.parsers.parsing_prop_table import parsing_prop_table
from sym_cps.representation.library import Library
from sym_cps.representation.library.elements.library_component import LibraryComponent
from sym_cps.representation.library.elements.perf_table import PerfTable


def parsing_prop_table(library: Library) -> dict[LibraryComponent, PerfTable]:
    table_dict = {}
    for propeller in library.components_in_type["Propeller"]:
        table = PerfTable(propeller=propeller)
        table_dict[propeller] = table
    return table_dict
