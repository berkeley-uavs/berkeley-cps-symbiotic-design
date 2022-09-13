# type: ignore
from sym_cps.representation.library import Library
from sym_cps.representation.library.elements.c_type import CType
from sym_cps.representation.tools.parsers.parse import parse_library_and_seed_designs


def different_properties(library: Library) -> dict[CType, set[str]]:
    missing_properties_from_c_types: dict[CType, set[str]] = dict()
    for c_type in library.component_types.values():
        properties = set()
        for component in c_type.belongs_to.values():
            if len(properties) == 0:
                properties = set(component.properties.keys())
            else:
                diff = set(component.properties.keys()) - properties
                if len(diff) > 0:
                    print(f"{c_type.id} has inconsistent properties across components")
                    if c_type in missing_properties_from_c_types.keys():
                        missing_properties_from_c_types[c_type] |= diff
                    else:
                        missing_properties_from_c_types[c_type] = diff
            list(component.properties.keys())
        print(c_type.parameters.keys())
    for c_type, properties in missing_properties_from_c_types.items():
        print(f"{c_type.id}: {str(properties)}")
    return missing_properties_from_c_types


def unknown_componnet_types(library: Library):
    for component in library.component_types["Unknown"].belongs_to.values():
        print(component.id)



if __name__ == "__main__":
    c_library, designs = parse_library_and_seed_designs()

    unknown_componnet_types(c_library)
    # different_properties(c_library)
