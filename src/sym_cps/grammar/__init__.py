from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from sym_cps.representation.design.abstract.elements.elements import AbstractComponent


@dataclass
class Grammar:
    rules: set[Rule]

    """TODO"""

    @classmethod
    def from_json(cls, grammar_json_path: Path) -> Grammar:
        return Grammar.from_dict(json.load(open(grammar_json_path)))

    @classmethod
    def from_dict(cls, grammar: dict) -> Grammar:
        """"TODO"""
        rules = set()
        """"e.g.."""
        for rule in grammar["RULES"]:
            new_rule = Rule.from_dict(rule)

        return cls(rules=rules)

    def learn_from_isomorphisms(self):
        """"TODO by Pier"""
        pass


@dataclass
class Rule:
    conditions: Condition
    production: set[AbstractComponent]

    """TODO"""

    @classmethod
    def from_dict(cls, topo: dict) -> Rule:
        """"TODO"""
        pass

    def to_contract(self):
        """TODO by Pier"""
        pass


@dataclass
class Condition:
    ego: set[Symbol]
    front: set[Symbol]
    bottom: set[Symbol]
    left: set[Symbol]
    right: set[Symbol]
    top: set[Symbol]
    rear: set[Symbol]


@dataclass
class Production:
    ego: set[Symbol]
    connections: set[Symbol]


@dataclass
class Symbol:
    terminal: bool
    element: AbstractComponent | NonTerminal


@dataclass
class NonTerminal:
    name: str
