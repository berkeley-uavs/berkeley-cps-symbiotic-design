from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from sym_cps.representation.design.abstract.elements.elements import AbstractComponent


@dataclass
class Structures:
    elements: set[Structure]

    def add_structure(self, structure: Structure):
        self.elements.add(structure)

    def learn_structures(self):
        """TODO by Pier"""
        pass


@dataclass
class Structure:
    name: str
    components: set[AbstractComponent]

    @classmethod
    def from_json(cls, structure_json_path: Path) -> Structure:
        return Structure.from_dict(json.load(open(structure_json_path)))

    @classmethod
    def from_dict(cls, topo: dict) -> Structure:
        """"TODO"""
        pass
