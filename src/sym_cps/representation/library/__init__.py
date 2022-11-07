import json
import os
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path

from sym_cps.representation.library.elements.c_connector import CConnector
from sym_cps.representation.library.elements.c_parameter import CParameter
from sym_cps.representation.library.elements.c_type import CType
from sym_cps.representation.library.elements.library_component import LibraryComponent
from sym_cps.representation.tools.parsers.parsing_library import fill_parameters_connectors, parse_components_and_types
from sym_cps.shared.paths import component_library_root_path_default, data_folder, component_selection_path


@dataclass
class Library:
    components: dict[str, LibraryComponent] = field(default_factory=dict)

    component_types: dict[str, CType] = field(init=False, default_factory=dict)
    components_in_type: dict[str, set[LibraryComponent]] = field(init=False, default_factory=dict)
    parameters: dict[str, CParameter] = field(init=False, default_factory=dict)
    connectors: dict[str, CConnector] = field(init=False, default_factory=dict)

    def __post_init__(self):
        self._update_data_structures()

    def _update_data_structures(self):
        for component in self.components.values():
            if component.comp_type.id not in self.component_types.keys():
                self.component_types[component.comp_type.id] = component.comp_type
                self.components_in_type[component.comp_type.id] = set()
            self.components_in_type[component.comp_type.id].add(component)
        for comp_type in self.component_types.values():
            if len(self.parameters) == 0:
                self.parameters = deepcopy(comp_type.parameters)
            else:
                self.parameters.update(comp_type.parameters)
            if len(self.connectors) == 0:
                self.connectors = deepcopy(comp_type.connectors)
            else:
                self.connectors.update(comp_type.connectors)

    def get_default_component(self, component_type: str, hub_size: int = 0) -> LibraryComponent:
        if component_type not in self.component_types.keys():
            raise Exception(f"{component_type}\nComponent Type not present in the library")
        f = open(component_selection_path)
        default = json.load(f)
        if component_type == "Hub":
            if hub_size == 4:
                component = self.components["0394od_para_hub_4"]
            elif hub_size == 3:
                component = self.components["0394od_para_hub_4"]
            else:
                raise Exception(f"No hub of size {hub_size}")
        else:
            component = self.components[default[component_type][0]]

        return component

    def get_connectors(
        self, component_type_a: CType, component_type_b: CType, direction: str
    ) -> (CConnector, CConnector):
        """TODO"""
        connectors_components_path = data_folder / "reverse_engineering" / "connectors_components_mapping.json"
        f = open(connectors_components_path)
        connections = json.load(f)

        name_a = component_type_a.id
        name_b = component_type_b.id
        results = ()

        available_components_a = list(connections[name_a].keys())
        if name_b in available_components_a:
            if direction == "":
                direction = "NONE"

            if direction in list(connections[name_a][name_b].keys()):
                connector_names = connections[name_a][name_b][direction]
                a_connector_name = connector_names[0]
                b_connector_name = connector_names[1]

                connector_a = self.connectors[a_connector_name]
                connector_b = self.connectors[b_connector_name]

                results = (connector_a, connector_b)

            else:
                print("illegal direction")

        else:
            print("illegal component")

        return results

    def update_information(
        self,
        connectable_connectors: dict[str, set[str]] | None,
        connectable_components_types: dict[CType, set[CType]] | None,
        design_parameters: dict[str, str] | None,
    ):
        if isinstance(connectable_connectors, dict):
            for key, value in connectable_connectors.items():
                for output_connector in value:  # type: ignore
                    if output_connector.id in self.connectors.keys():
                        # print(f"{key} -> {output_connector}")
                        self.connectors[key]._update_field("compatible_with", {output_connector.id: output_connector})

        if isinstance(connectable_components_types, dict):
            for key, value in connectable_components_types.items():
                for compatible_class in value:  # type: ignore
                    self.component_types[key.id]._update_field(
                        "compatible_with", {compatible_class.id: compatible_class}
                    )

        if isinstance(design_parameters, dict):
            for key, value in design_parameters.items():
                if key not in self.parameters:
                    print(f"{key} is missing")
                else:
                    self.parameters[key]._edit_field("design_parameter", value)

    @classmethod
    def from_folder(cls, path: Path | None = None):
        if path is None:
            path = component_library_root_path_default
        print(f"Reading from {path}")
        file_name_list = os.listdir(path)

        components: dict[str, LibraryComponent] = {}

        for name in file_name_list:
            file_path = path / name
            if os.path.isfile(file_path):
                components.update(parse_components_and_types(file_path))

        for name in file_name_list:
            file_path = path / name
            if os.path.isfile(file_path):
                components.update(fill_parameters_connectors(file_path, components))

        return Library(components)

    def __str__(self):
        return "\n+++++++++++++++++++++++++++++++++\n".join(str(c) for c in list(self.components.values()))
