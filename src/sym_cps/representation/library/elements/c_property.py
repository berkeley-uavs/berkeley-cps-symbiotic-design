from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sym_cps.representation.library.elements.library_component import LibraryComponent


@dataclass(frozen=True)
class CProperty:
    name: str
    value: str | float
    belongs_to: LibraryComponent

    def __str__(self):
        return f"{self.name}: {self.value}"

    @property
    def export(self) -> dict:
        ret = {}
        ret["name"] = self.name
        ret["value"] = str(self.value)
        return ret
