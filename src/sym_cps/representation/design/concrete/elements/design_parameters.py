from __future__ import annotations

from dataclasses import dataclass, field

from sym_cps.representation.design.concrete.elements.parameter import Parameter


@dataclass
class DesignParameter:
    id: str
    parameters: set[Parameter]

    _value: float = field(init=False)

    def __post_init__(self):
        values = set([p.value for p in self.parameters])
        if len(values) > 1:
            raise AttributeError("All parameters in DesignParameter must have the same value")
        self._value = next(iter(values))

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value: float):
        for parameter in self.parameters:
            parameter.value = value
        self._value = value

    def add(self, parameter: Parameter):
        self.parameters.add(parameter)

    def remove(self, parameter: Parameter):
        self.parameters.remove(parameter)

    def __str__(self):
        ret = f"{self.id} = {list(self.parameters)[0].value}:\n"
        for param in self.parameters:
            ret += f"\t{param.id}\n"
        return ret

    def __hash__(self):
        return hash(self.id)
