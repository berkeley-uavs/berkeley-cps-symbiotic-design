from __future__ import annotations

from dataclasses import dataclass, field

from sym_cps.representation.design.concrete.elements.parameter import Parameter
from sym_cps.representation.library.elements.c_parameter import CParameter
from sym_cps.representation.library.elements.c_property import CProperty
from sym_cps.representation.library.elements.c_type import CType
from sym_cps.representation.library.elements.library_component import LibraryComponent


@dataclass(frozen=True)
class Component:
    id: str

    library_component: LibraryComponent

    parameters: dict[str, Parameter] = field(default_factory=dict)

    def __post_init__(self):
        """Fill up all the parameters with the assigned_value, or default_value"""
        for parameter_accepted in self.configurable_parameters:
            if parameter_accepted.id not in self.parameters.keys():
                if "assigned_val" in parameter_accepted.values.keys():
                    new_parameter = Parameter(
                        value=float(parameter_accepted.values["assigned_val"]),
                        c_parameter=parameter_accepted,
                        component=self,
                    )
                elif "default_val" in parameter_accepted.values.keys():
                    new_parameter = Parameter(
                        value=float(parameter_accepted.values["default_val"]),
                        c_parameter=parameter_accepted,
                        component=self,
                    )
                else:
                    raise Exception(
                        f"Parameter {parameter_accepted.id} does not have assigned_val nor default_val"
                    )
                self.parameters[parameter_accepted.id] = new_parameter
            for parameter in self.parameters.values():
                parameter.component = self

    @property
    def model(self) -> str:
        return self.library_component.id

    @property
    def c_type(self) -> CType:
        return self.library_component.comp_type

    @property
    def properties(self) -> dict[str, CProperty]:
        return self.library_component.properties

    @property
    def configurable_parameters(self) -> set[CParameter]:
        """Returns the set of all ParameterType that can be configured in the Component"""
        return set(self.library_component.parameters.values())

    @property
    def params_props_values(self) -> dict[str, float | str]:
        """Returns dictionary: with the values of each parameter and property of the component"""
        params_props_values: dict[str, float | str] = {}

        for param_id, parameter in self.parameters.items():
            params_props_values[param_id] = parameter.value
        for property_id, property in self.properties.items():
            params_props_values[property_id] = property.value

        return params_props_values

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

        if self.params_props_values != self.params_props_values:
            return False

        return True

    def __ne__(self, other: object):
        if not isinstance(other, Component):
            return NotImplemented

        return not self.__eq__(other)

    def __hash__(self):
        return abs(hash(self.id))

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
