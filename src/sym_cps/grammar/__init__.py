from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from sym_cps.grammar.symbols import Symbol
from sym_cps.shared.paths import grammar_rules_path


@dataclass
class Grammar:
    rules: set[Rule]

    """TODO"""

    @classmethod
    def from_json(cls, grammar_json_path: Path) -> Grammar:
        return Grammar.from_dict(json.load(open(grammar_json_path)))

    @classmethod
    def from_dict(cls, grammar: dict) -> Grammar:
        """ "TODO"""
        rules = set()
        """"e.g.."""
        for rule in grammar["RULES"]:
            new_rule = Rule.from_dict(rule)

        return cls(rules=rules)

    def learn_from_isomorphisms(self):
        """ "TODO by Pier"""


@dataclass
class Rule:
    conditions: set[Condition]
    production: Production

    """TODO"""

    @classmethod
    def from_dict(cls, topo: dict) -> Rule:
        """ "TODO"""

    def to_contract(self):
        """TODO by Pier"""


@dataclass
class Condition:
    ego: set[Symbol]
    front: set[Symbol]
    bottom: set[Symbol]
    left: set[Symbol]
    right: set[Symbol]
    top: set[Symbol]
    rear: set[Symbol]

    def matches(
            self, ego: Symbol, front: Symbol, bottom: Symbol, left: Symbol, right: Symbol, top: Symbol, rear: Symbol
    ):
        return (
                ego in self.ego
                and front in self.front
                and bottom in self.bottom
                and left in self.left
                and right in self.right
                and top in self.top
                and rear in self.rear
        )


@dataclass
class Production:
    ego: Symbol
    connections: set[Symbol]




if __name__ == '__main__':
    grammar = Grammar.from_json(grammar_json_path=grammar_rules_path)
