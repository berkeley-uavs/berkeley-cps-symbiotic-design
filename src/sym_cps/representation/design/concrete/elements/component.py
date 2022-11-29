from __future__ import annotations

import json
from dataclasses import dataclass, field

from sym_cps.representation.design.concrete.elements.parameter import Parameter
from sym_cps.representation.library.elements.c_parameter import CParameter
from sym_cps.representation.library.elements.c_property import CProperty
from sym_cps.representation.library.elements.c_type import CType
from sym_cps.representation.library.elements.library_component import LibraryComponent
from sym_cps.shared.library import c_library
from sym_cps.shared.paths import learned_default_params_path


@dataclass(frozen=False)
class Component:
    c_type: CType | None = None

    id: str | None = None

    library_component: LibraryComponent | None = None

    parameters: dict[str, Parameter] = field(default_factory=dict)

    def __post_init__(self):
        """Fill up all the parameters with the assigned_value, or default_value"""
        if self.c_type is None and self.library_component is None:
            raise AttributeError
        if self.c_type is None:
            self.c_type = self.library_component.comp_type
        for parameter_accepted in self.configurable_parameters:
            if parameter_accepted.id not in self.parameters.keys():
                new_parameter = Parameter(
                    value=float(parameter_accepted.default),
                    c_parameter=parameter_accepted,
                    component=self,
                )
                self.parameters[parameter_accepted.id] = new_parameter
            for parameter in self.parameters.values():
                parameter.component = self

    def choose_default(self):
        self.library_component = c_library.get_default_component(self.c_type.id)

    @property
    def model(self) -> str | None:
        if self.library_component is not None:
            return self.library_component.id
        return None

    @property
    def properties(self) -> dict[str, CProperty] | None:
        if self.library_component is not None:
            return self.library_component.properties
        return None

    @property
    def configurable_parameters(self) -> set[CParameter]:
        """Returns the set of all ParameterType that can be configured in the Component"""
        return set(self.c_type.parameters.values())

    @property
    def params_props_values(self) -> dict[str, float | str]:
        """Returns dictionary: with the values of each parameter and property of the component"""
        params_props_values: dict[str, float | str] = {}

        for param_id, parameter in self.parameters.items():
            params_props_values[param_id] = parameter.value
        for property_id, property in self.properties.items():
            params_props_values[property_id] = property.value

        return params_props_values

    @property
    def params_values(self) -> dict[str, float]:
        params_values: dict[str, float] = {}

        for param_id, parameter in self.parameters.items():
            params_values[param_id] = parameter.value

        return params_values

    @property
    def params_values_not_default(self) -> dict[str, float]:
        params_values: dict[str, float] = {}
        default_parameters: dict = json.load(open(learned_default_params_path))
        for param_id, parameter in self.parameters.items():
            if param_id in default_parameters.keys():
                if default_parameters[param_id] == parameter.value:
                    continue
            params_values[param_id] = parameter.value

        return params_values

    def update_parameters(self, parameters: dict[str, float]):
        for param_id, value in parameters.items():
            self.parameters[param_id].value = value

    def set_shared_parameters(self):
        # print("Setting default parameters...")
        for param_id, parameter in self.parameters.items():
            default_parameters: dict = json.load(open(learned_default_params_path))

            if param_id in default_parameters:
                self.parameters[param_id].value = float(default_parameters[param_id])

    def _edit_field(self, name, value):
        object.__setattr__(self, name, value)

    def _update_field(self, name, value):
        attr = object.__getattribute__(self, name)
        attr.update(value)
        object.__setattr__(self, name, attr)

    def __eq__(self, other: object):

        if not isinstance(other, Component):
            return NotImplemented

        if self.library_component != other.library_component:
            return False

        if self.params_props_values != other.params_props_values:
            return False

        return True

    def __ne__(self, other: object):
        if not isinstance(other, Component):
            return NotImplemented

        return not self.__eq__(other)

    def __hash__(self):
        _parameters_hash = ""
        for para in self.parameters.values():
            _parameters_hash += str(para.value)
        # return hash(self.library_component.id + _parameters_hash)
        return hash(self.id + _parameters_hash)

    def __str__(self):
        s1 = f"name: {self.model}\n" f"type: {self.c_type}\n"

        parameters_str = []
        for k, v in self.parameters.items():
            parameters_str.append(f"\t{k}: {v}")
        parameters = "\n".join(parameters_str)

        if len(parameters_str) != 0:
            s2 = f"parameters:\n{parameters}\n"
        else:
            s2 = ""

        return s1 + s2
