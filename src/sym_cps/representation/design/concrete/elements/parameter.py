from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from sym_cps.representation.library.elements.c_parameter import CParameter

if TYPE_CHECKING:
    from sym_cps.representation.design.concrete.elements.component import Component


@dataclass
class Parameter:
    value: float
    c_parameter: CParameter
    component: Component | None = None

    @property
    def min(self) -> float:
        return self.c_parameter.values["min_val"]

    @property
    def max(self) -> float:
        return self.c_parameter.values["max_val"]

    def __str__(self):
        if self.component is not None:
            return f"{self.component.id}_{self.c_parameter.id}: {self.value}"
        return f"{self.c_parameter.id}: {self.value}"

    def __hash__(self):
        return hash(self.__str__())
    
    @property
    def id(self) -> str:
        return f"{self.component.id}_{self.c_parameter.id}"
