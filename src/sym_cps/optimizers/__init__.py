from dataclasses import dataclass
from enum import Enum, auto

from sym_cps.representation.library import Library, LibraryComponent


class OptimizationStrategy(Enum):
    random_strategy = auto()


@dataclass(frozen=True)
class Optimizer:
    library: Library

    def choose_component(self, component_type_id: str, design_name: str = "") -> LibraryComponent:
        """Choose Component and its Parameters"""
        default_component: LibraryComponent = self.library.get_default_component(component_type_id, design_name)
        return default_component
