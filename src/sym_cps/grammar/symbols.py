from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass

from sym_cps.shared.paths import grammar_rules_path


@dataclass(frozen=True)
class Symbol:
    pass

    @property
    @abstractmethod
    def is_terminal(self):
        pass

    @property
    def is_start(self):
        return False


@dataclass(frozen=True)
class TSymbol(Symbol):
    """Terminal Symbol"""

    @property
    def is_terminal(self):
        return True


@dataclass(frozen=True)
class NTSymbol(Symbol):
    """Non-Terminal Symbol"""

    @property
    def is_terminal(self):
        return False


@dataclass(frozen=True)
class Unoccupied(NTSymbol):
    pass


@dataclass(frozen=True)
class Fuselage(TSymbol):
    pass


@dataclass(frozen=True)
class Rotor(TSymbol):
    pass


@dataclass(frozen=True)
class Connector(TSymbol):
    pass


@dataclass(frozen=True)
class Empty(TSymbol):
    pass
