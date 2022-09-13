from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from sym_cps.representation.tools.ids import parameter_id

if TYPE_CHECKING:
    from sym_cps.representation.library.elements.library_component import CType


@dataclass(frozen=True)
class CParameter:
    """Indicates the possible values and type of a component parameter.
    Parameters are associated to component classes.
    """

    name: str

    belongs_to: CType = field(init=False)

    _values: dict = field(init=False, default_factory=dict)

    def _edit_field(self, name, value):
        object.__setattr__(self, name, value)

    def _update_field(self, name, value):
        attr = object.__getattribute__(self, name)
        attr.update(value)
        object.__setattr__(self, name, attr)

    def __post_init__(self):
        vals: dict[str, float | None] = {
            "min_val": None,
            "max_val": None,
            "default_val": None,
            "assigned_val": None,
        }
        self._edit_field("_values", vals)

    @property
    def values(self) -> dict[str, float]:
        """Filters out None component"""
        return {key: value for key, value in self._values.items() if value is not None}

    def _edit_values(self, values: dict):
        for key in values.keys():
            if key in self._values.keys():
                if values[key] != "":
                    self._values[key] = float(values[key])

    @property
    def id(self) -> str:
        """Internal ID"""
        return parameter_id(self.name, str(self.belongs_to))

    def __str__(self):
        values = ", ".join([f"{k}: {v}" for k, v in self.values.items()])
        return f"{self.name}\t {values}"

    def __hash__(self):
        return abs(hash(self.id))
