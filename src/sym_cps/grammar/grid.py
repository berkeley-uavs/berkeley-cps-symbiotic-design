from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from sym_cps.grammar import Grammar, Symbol, SymbolConnection


@dataclass
class AbstractGrid:
    nodes: list[list[list[str]]]
    adjacencies: dict[tuple, list[tuple]]
    name: str = ""

    def __hash__(self):
        return hashlib.sha1((str(self.nodes) + str(self.adjacencies)).encode("utf-8"))

    @property
    def id(self):
        return str(self.__hash__())[:10]

    @property
    def n_wings(self):
        return str(self.nodes).count("WING")

    @property
    def n_props(self):
        return str(self.nodes).count("ROTOR")


@dataclass
class Grid:
    nodes: list[list[list[Symbol]]]
    connections: set[SymbolConnection] = field(default_factory=set)
    name: str = ""

    @classmethod
    def generate_from_grammar(cls, grammar: Grammar) -> Grid:
        """TODO:"""
