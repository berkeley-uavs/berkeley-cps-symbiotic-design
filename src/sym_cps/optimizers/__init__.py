from dataclasses import dataclass
from enum import Enum, auto

# from sym_cps.representation.design.concrete import DConcrete
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
    #
    # def component_selection(self, d_concrete: DConcrete,
    #                               body_weight = 0,
    #                               timeout_millisecond = 100000,
    #                               max_iter = 100):
    #     from sym_cps.contract.component_selection import ComponentSelectionContract
    #     self.component_selection = ComponentSelectionContract(c_library=self.library)
    #     propeller, motor, battery = self.component_selection.select_hackathon(
    #         design_concrete=d_concrete, max_iter=max_iter, timeout_millisecond=timeout_millisecond, body_weight=body_weight
    #     )
    #     if propeller is None or motor is None or battery is None:
    #         print("Cannot find a valid component within the time constraints.....")
    #     else:
    #         self.component_selection.replace_with_component(
    #             design_concrete=d_concrete, propeller=propeller, motor=motor, battery=battery
    #         )
    #     return d_concrete