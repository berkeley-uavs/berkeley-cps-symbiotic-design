import abc
import json
from dataclasses import dataclass, field

from sym_cps.shared.paths import grammar_rules_path

rule_dict = json.load(open(grammar_rules_path))


class Grid:
    nodes: list[list[list[str]]]
    adjacencies: dict[tuple, list[tuple]]


@dataclass
class AbstractComponent(abc.ABC):
    base_name: str
    instance_id: str
    connections: {} = field(default_factory=dict)
    parameters: {} = field(default_factory=dict)


@dataclass
class Fuselage(AbstractComponent):
    instance_n: int = 1

    def __post_init__(self):
        self.base_name = "Fuselage_str"
        self.instance_id = f"Fuselage_str_instance_{self.instance_n}"


@dataclass
class Propeller(AbstractComponent):
    instance_n: int = 1

    def __post_init__(self):
        self.base_name = "Propeller_str"
        self.instance_id = f"Propeller_str_instance_{self.instance_n}"


@dataclass
class Wing(AbstractComponent):
    instance_n: int = 1

    def __post_init__(self):
        self.base_name = "Wing"
        self.instance_id = f"Wing_instance_{self.instance_n}"


@dataclass
class Tube(AbstractComponent):
    instance_n: int = 1

    def __post_init__(self):
        self.base_name = "Tube"
        self.instance_id = f"Tube_instance_{self.instance_n}"


@dataclass
class Hub(AbstractComponent):
    instance_n: int = 1

    def __post_init__(self):
        self.base_name = "Hub"
        self.instance_id = f"Hub_instance_{self.instance_n}"


@dataclass
class AbstractConnection:
    elements: tuple[AbstractComponent, AbstractComponent, int]


@dataclass
class AbstractDesign:
    connections: list[AbstractConnection] = field(default_factory=list)

    @classmethod
    def from_grid(cls, grid: Grid):
        pass
