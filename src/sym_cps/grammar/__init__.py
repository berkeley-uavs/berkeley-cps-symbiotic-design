from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from aenum import Enum, auto
from sym_cps.grammar.symbols import Symbol, Unoccupied
from sym_cps.shared.paths import grammar_rules_path


class Direction(Enum):
    ego = auto()
    front = auto()
    bottom = auto()
    left = auto()
    right = auto()
    top = auto()
    rear = auto()


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
    conditions: set[ConditionSet]
    production: Production

    """TODO"""

    def matches(self, state: State) -> State | None:
        for condition in self.conditions:
            if condition.matches(state):
                return self.production.apply(state)
        return None

    @classmethod
    def from_dict(cls, topo: dict) -> Rule:
        """ "TODO"""

    def to_contract(self):
        """TODO by Pier"""


@dataclass
class ConditionSet:
    ego: Unoccupied
    front: set[Symbol]
    bottom: set[Symbol]
    left: set[Symbol]
    right: set[Symbol]
    top: set[Symbol]
    rear: set[Symbol]

    def matches(self, state: State
                ):
        return (
                state.ego in self.ego
                and state.front in self.front
                and state.bottom in self.bottom
                and state.left in self.left
                and state.right in self.right
                and state.top in self.top
                and state.rear in self.rear
        )


@dataclass
class SymbolConnection:
    symbol_a: Symbol
    symbol_b: Symbol


@dataclass
class State:
    ego: Symbol
    front: Symbol
    bottom: Symbol
    left: Symbol
    right: Symbol
    top: Symbol
    rear: Symbol

    connections: set[SymbolConnection] = field(default_factory=set)


@dataclass
class Production:
    ego: Symbol
    edge: Direction | None

    def apply(self, state: State) -> State:
        state.ego = self.ego
        if self.edge is not None:
            connection = SymbolConnection(self.ego, getattr(state, self.edge.name))
            state.connections.add(connection)
        return state


if __name__ == '__main__':
    grammar = Grammar.from_json(grammar_json_path=grammar_rules_path)
