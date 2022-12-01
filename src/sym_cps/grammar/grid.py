from __future__ import annotations
from dataclasses import dataclass, field

from sym_cps.grammar import Symbol, SymbolConnection, Grammar


@dataclass
class Grid:
    nodes: list[list[list[Symbol]]]
    connections: set[SymbolConnection] = field(default_factory=set)
    name: str = ""

    @classmethod
    def generate_from_grammar(cls, grammar: Grammar) -> Grid:
        """TODO:"""
