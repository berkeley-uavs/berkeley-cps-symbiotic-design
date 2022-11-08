from sym_cps.shared.designs import designs
from sym_cps.shared.library import c_library
from sym_cps.tools.update_library import update_dat_files_and_export


def update_library_to_db():
    for id, library_component in c_library.components.items():
        """TODO IMPLEMENT"""
        id = library_component.id
        c_type_id = library_component.comp_type.id

    for component_type in c_library.component_types:
        """TODO IMPLEMENT"""


def update_designs_to_db():
    for design_id, (dconcrete, dtopology) in designs.items():
        for component in dconcrete.components:
            for parameter in component.parameters.values():
                parameter.value
                """TODO"""


if __name__ == "__main__":
    update_dat_files_and_export()
    update_library_to_db()
    update_designs_to_db()
