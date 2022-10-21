from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from sym_cps.representation.library.elements.c_connector import CConnector
from sym_cps.representation.library.elements.c_property import CProperty
from sym_cps.representation.library.elements.c_type import CType
from sym_cps.tools.strings import tab

if TYPE_CHECKING:
    from sym_cps.representation.design.concrete.elements.parameter import CParameter


@dataclass(frozen=True)
class LibraryComponent:
    """Represent and model of component in the components_library.
    It has fixed properties and can have parameters and connectors."""

    """Component Model Name"""
    id: str

    comp_type: CType

    properties: dict[str, CProperty] = field(init=False, default_factory=dict)

    @property
    def id_with_type(self) -> str:
        return f"{self.id} [{self.comp_type.id}]"

    @property
    def parameters(self) -> dict[str, CParameter]:
        return self.comp_type.parameters

    @property
    def connectors(self) -> dict[str, CConnector]:
        return self.comp_type.connectors

    def _edit_field(self, name, value):
        object.__setattr__(self, name, value)

    def _update_field(self, name, value):
        attr = object.__getattribute__(self, name)
        attr.update(value)
        object.__setattr__(self, name, attr)

    def __hash__(self):
        return hash(str(self.id))

    def __eq__(self, other: object):

        if not isinstance(other, LibraryComponent):
            raise Exception("Different classes")

        return self.id == other.id

    def __str__(self) -> str:
        s1 = f"name: {self.id}\n" f"type: {str(self.comp_type)}\n"

        properties_str = []
        for e in list(self.properties.values()):
            properties_str.append(tab(e))
        properties = "\n".join(properties_str)

        parameters_str = []
        for e in list(self.parameters.values()):
            parameters_str.append(tab(e))
        parameters = "\n".join(parameters_str)

        connectors_str = []
        for e in list(self.connectors.values()):
            connectors_str.append(tab(e))

        connectors = "\n".join(connectors_str)

        s2 = f"properties:\n{properties}\n"
        s3 = f"connectors:\n{connectors}\n"
        s4 = f"parameters:\n{parameters}\n"

        return s1 + s2 + s3 + s4
