# type: ignore
import json

from sym_cps.representation.design.concrete import DConcrete
from sym_cps.representation.design.topology import DTopology
from sym_cps.representation.library import CConnector, CType, Library
from sym_cps.representation.tools.parsers.parsing_library import (
    all_parameters_lower_bounds,
    all_parameters_upper_bounds,
)
from sym_cps.shared.library import c_library
from sym_cps.shared.paths import library_folder
from sym_cps.tools.io import save_to_file
from sym_cps.tools.persistance import load
from sym_cps.tools.strings import repr_dictionary


def export_library():
    print("Exporting library...")
    for component_type, components in c_library.components_in_type.items():
        comp_type_dict = {}
        for component in components:
            comp_type_dict[component.id] = component.export
        save_to_file(comp_type_dict, f"{component_type}s.json", folder_name="library/components")
    save_to_file(c_library.export("components"), "library_components.json", folder_name="library")
    save_to_file(c_library.export("connectors"), "library_connectors.json", folder_name="library")
    save_to_file(c_library.export("parameters"), "library_parameters.json", folder_name="library")


def analysis(library_dat_file: str = "library.dat", designs_dat_file: str = "designs.dat"):
    c_library: Library = load(library_dat_file)  # type: ignore

    all_types_in_library = set(c_library.component_types.keys())
    all_components_types_in_designs = set()
    shared_component_types_in_designs = set()

    components_types_in_design = {}
    components_types_and_model_in_design = {}
    component_used_in_designs = {}

    designs: dict[str, tuple[DConcrete, DTopology]] = load(designs_dat_file)  # type: ignore
    for design_id, (dconcrete, dtopology) in designs.items():
        component_types = set()
        components_types_and_model_in_design[design_id] = dconcrete.get_components_summary
        for component in dconcrete.components:
            component_types.add(component.c_type.id)
            if component.c_type.id not in component_used_in_designs.keys():
                component_used_in_designs[component.c_type.id] = []
            if component.model not in component_used_in_designs[component.c_type.id]:
                component_used_in_designs[component.c_type.id].append(component.model)
        all_components_types_in_designs |= component_types
        if len(shared_component_types_in_designs) == 0:
            shared_component_types_in_designs |= component_types
        else:
            shared_component_types_in_designs = shared_component_types_in_designs.intersection(component_types)
        components_types_in_design[design_id] = list(component_types)

    unused_types = all_types_in_library - all_components_types_in_designs

    # save_to_file("\n".join(list(all_components_types_in_designs)),
    #              "component_types_in_seed_designs.txt",
    #              folder_name="library"
    #              )
    #
    # save_to_file("\n".join(list(unused_types)),
    #              "unused_types.txt",
    #              folder_name="library"
    #              )

    types_in_use = {}
    for comp_type in all_components_types_in_designs:
        types_in_use[comp_type] = comp_type

    # types_in_use_json = json.dumps(types_in_use, indent=4)
    #
    # save_to_file(types_in_use_json,
    #              "types_renaming.json",
    #              folder_name="library"
    #              )

    components_types_in_design_json = json.dumps(components_types_in_design, indent=4)

    save_to_file(components_types_in_design_json,
                 "components_types_in_design.json",
                 folder_name="library"
                 )
    component_used_in_designs_json = json.dumps(component_used_in_designs, indent=4)
    save_to_file(component_used_in_designs_json,
                 "component_choice_in_designs.json",
                 folder_name="library"
                 )

    # components_types_and_model_in_design_json = json.dumps(components_types_and_model_in_design, indent=4)
    # save_to_file(components_types_and_model_in_design_json,
    #              "components_types_and_model_in_design.json",
    #              folder_name="library"
    #              )


def generate_tables(library_dat_file: str = "library.dat"):
    c_library: Library = load(library_dat_file)  # type: ignore

    all_types_tables = []
    for component_type in c_library.component_types.values():
        c_type_table = []
        c_table_header = [component_type.id]
        for parameter in component_type.parameters.values():
            c_table_header.append(parameter.id)
        c_type_table.append(c_table_header)
        for component in c_library.components_in_type[component_type.id]:
            entry = [component.id]
            for parameter_id in c_table_header[1:]:
                entry.append(component.parameters[parameter_id].summary)
            c_type_table.append(entry)
        all_types_tables.append(c_type_table)

    for table in all_types_tables:
        print(table[0])


if __name__ == "__main__":
    export_library()
    # update_dat_files_and_export()
    # export_library()
