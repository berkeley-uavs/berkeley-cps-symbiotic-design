from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sym_cps.representation.library.elements.c_connector import CConnector
    from sym_cps.representation.library.elements.c_parameter import CParameter
    from sym_cps.representation.library.elements.library_component import LibraryComponent


@dataclass(frozen=True)
class CType:
    id: str

    """Configurable parameters"""
    parameters: dict[str, CParameter] = field(init=False, default_factory=dict)

    """Accepted connectors"""
    connectors: dict[str, CConnector] = field(init=False, default_factory=dict)

    """Compatible CType to be connected to"""
    compatible_with: dict[str, CType] = field(init=False, default_factory=dict)

    """Library components of CType"""
    belongs_to: dict[str, LibraryComponent] = field(init=False, default_factory=dict)

    def _edit_field(self, name, value):
        object.__setattr__(self, name, value)

    def _update_field(self, name, value):
        attr = object.__getattribute__(self, name)
        if len(attr) == 0:
            object.__setattr__(self, name, value)
            return
        attr.update(value)
        object.__setattr__(self, name, attr)

    def _remove_from_field(self, name, value):
        if value not in self.belongs_to.keys():
            return
        attr = object.__getattribute__(self, name)
        if len(attr) == 0:
            return
        del attr[value]
        object.__setattr__(self, name, attr)

    @property
    def export(self) -> dict:
        ret = {}
        ret["id"] = self.id
        ret["properties"] = {}
        for parameter_id, parameter in self.parameters.items():
            ret["properties"][parameter_id] = parameter.export
        ret["connectors"] = {}
        for connector_id, connector in self.connectors.items():
            ret["connectors"][connector_id] = connector.export
        return ret

    def __str__(self) -> str:
        return self.id

    def __hash__(self) -> int:
        return hash(self.id)
