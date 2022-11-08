from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from sym_cps.representation.tools.ids import connector_id

if TYPE_CHECKING:
    from sym_cps.representation.library.elements.c_type import CType


@dataclass
class CConnector:

    name: str

    belongs_to: CType

    compatible_with: dict[str, CConnector] = field(init=False, default_factory=dict)

    def _edit_field(self, name, value):
        object.__setattr__(self, name, value)

    def _update_field(self, name, value):
        attr = object.__getattribute__(self, name)
        attr.update(value)
        object.__setattr__(self, name, attr)

    @property
    def id(self) -> str:
        return connector_id(self.name, str(self.belongs_to))

    def __hash__(self):
        return hash(self.id)

    @property
    def export(self) -> dict:
        ret = {}
        ret["name"] = self.name
        ret["compatible_with"] = list(self.compatible_with.keys())
        return ret


    def __str__(self):
        s = f"Connector_ID:\t{self.id}\n"
        if len(self.compatible_with) != 0:
            s = s + f"\tCONNECTABLE_WITH:\t{', '.join(self.compatible_with.keys())}\n"
        return s
