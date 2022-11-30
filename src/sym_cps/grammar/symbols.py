from __future__ import annotations

from dataclasses import dataclass

from sym_cps.shared.paths import grammar_rules_path


@dataclass
class Symbol:
    terminal: bool = False


@dataclass
class Unoccupied(Symbol):
    terminal: bool = False


@dataclass
class Empty(Symbol):
    terminal: bool = False


@dataclass
class Body(Symbol):
    terminal: bool = False


@dataclass
class Fuselage(Body):
    terminal: bool = False


@dataclass
class Body(Symbol):
    terminal: bool = False


@dataclass
class A(Group):
    terminal: bool = False


@dataclass
class A(Group):
    terminal: bool = False


@dataclass
class G(Group):
    terminal: bool = False


if __name__ == '__main__':
    grammar = Grammar.from_json(grammar_json_path=grammar_rules_path)
