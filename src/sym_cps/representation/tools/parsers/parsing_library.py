import json
from pathlib import Path

from sym_cps.representation.library.elements.c_connector import CConnector
from sym_cps.representation.library.elements.c_parameter import CParameter
from sym_cps.representation.library.elements.c_property import CProperty
from sym_cps.representation.library.elements.c_type import CType
from sym_cps.representation.library.elements.library_component import LibraryComponent
from sym_cps.representation.tools.ids import connector_id, parameter_id
from sym_cps.representation.tools.parsers.temp_objects import (
    all_component_types,
    all_connectors,
    all_library_components,
    all_parameters,
)
from sym_cps.shared.paths import lower_bound_file, upper_bound_file
from sym_cps.tools.strings import rename_component_types

# Maps all parameter_ids to (min,max) bounds"""

all_parameters_upper_bounds: dict[str, float] = {}
all_parameters_lower_bounds: dict[str, float] = {}


def parse_components_and_types(path: Path) -> dict[str, LibraryComponent]:
    parse_parameter_bounds()

    print(f"Reading Library File: {path}")

    components: dict[str, LibraryComponent] = {}

    if "unknown" not in all_component_types:
        all_component_types["unknown"] = CType("Unknown")

    with open(path, "r") as file:
        info_dict = json.load(file)
        for entry in info_dict:
            component_name = entry["comp"]
            if component_name not in all_library_components.keys():
                library_component = LibraryComponent(id=component_name, comp_type=all_component_types["unknown"])
                all_component_types["unknown"]._update_field("belongs_to", {library_component.id: library_component})
                all_library_components[component_name] = library_component
            else:
                library_component = all_library_components[component_name]
            components[component_name] = library_component
            if "class" in entry.keys():
                type_name = entry["class"]
                component_id = entry["comp"]
                if "para_hub" in component_id:
                    n = component_id[-1]
                    type_name = f"{type_name}{n}"

                if "Passenger" == type_name:
                    pass
                if type_name not in all_component_types.keys():
                    all_component_types[type_name] = CType(id=rename_component_types(type_name))

                c_type = all_component_types[type_name]

                library_component._edit_field("comp_type", c_type)
                all_component_types["unknown"]._remove_from_field("belongs_to", library_component.id)
                c_type._update_field("belongs_to", {library_component.id: library_component})

            if "prop" in entry.keys():
                if "prop_val" in entry.keys():
                    try:
                        value = float(entry["prop_val"])
                    except Exception:
                        value = entry["prop_val"]

                    comp_property = CProperty(entry["prop"], value, library_component)
                    library_component._update_field("properties", {comp_property.name: comp_property})
                else:
                    pass

            if "conn" in entry.keys():
                pass

    return components


def fill_parameters_connectors(path: Path, components: dict[str, LibraryComponent]) -> dict[str, LibraryComponent]:

    with open(path, "r") as file:
        info_dict = json.load(file)
        for entry in info_dict:
            component_name = entry["comp"]
            if component_name not in all_library_components.keys():
                library_component = LibraryComponent(id=component_name, comp_type=all_component_types["unknown"])
                all_library_components[component_name] = library_component
            else:
                library_component = all_library_components[component_name]
            components[component_name] = library_component
            if "class" in entry.keys():
                pass

            if "prop" in entry.keys():
                if "prop_val" in entry.keys():
                    pass
                else:
                    # print(library_component.comp_type)
                    param_id = parameter_id(entry["prop"], str(library_component.comp_type))

                    if "min" not in entry.keys():
                        try:
                            if param_id in all_parameters_lower_bounds.keys():
                                entry["min_val"] = all_parameters_lower_bounds[param_id]
                        except KeyError:
                            pass
                            # print(f"WARNING: Parameter {param_id} does not have any lower bound")

                    if "max" not in entry.keys():
                        try:
                            entry["max_val"] = all_parameters_upper_bounds[param_id]
                        except KeyError:
                            pass
                            # print(f"WARNING: Parameter {param_id} does not have any upper bound")

                    if param_id not in all_parameters.keys():
                        all_parameters[param_id] = CParameter(entry["prop"])

                    cparam = all_parameters[param_id]
                    cparam._edit_values(entry)
                    cparam._edit_field("belongs_to", library_component.comp_type)
                    library_component.comp_type._update_field("parameters", {cparam.id: cparam})

            if "conn" in entry.keys():
                if "Connector" == entry["conn"]:
                    pass
                conn_id = connector_id(entry["conn"], str(library_component.comp_type))
                if conn_id not in all_connectors.keys():
                    all_connectors[conn_id] = CConnector(entry["conn"], library_component.comp_type)
                connector = all_connectors[conn_id]
                library_component.comp_type._update_field("connectors", {connector.id: connector})

    return components


def parse_parameter_bounds() -> None:
    """Parse design expert parameter bounds from 'lower_bound_file' 'lower_bound_file'"""

    if len(all_parameters_lower_bounds) == 0:

        file = open(lower_bound_file, "r")
        for line in file:
            k, v = line.strip().split(":")
            all_parameters_lower_bounds[k.strip()] = float(v.strip())

    if len(all_parameters_upper_bounds) == 0:
        file = open(upper_bound_file, "r")
        for line in file:
            k, v = line.strip().split(":")
            all_parameters_upper_bounds[k.strip()] = float(v.strip())
