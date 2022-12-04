from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from sym_cps.representation.design.concrete import Component, Connection
from sym_cps.shared.library import c_library
from sym_cps.shared.paths import structures_path
from sym_cps.tools.strings import get_instance_name

if TYPE_CHECKING:
    from sym_cps.representation.design.abstract import AbstractConnection


@dataclass
class AbstractComponent:
    """
    Element of a 3D grid. A structure of multiple 'Component'
    """

    grid_position: tuple[int, int, int]
    base_name: str = ""
    instance_n: int = 1
    abstract_connections: set[AbstractConnection] = field(default_factory=set)
    color: str = "black"
    structure: set[Component] = field(default_factory=set)
    connections: set[Connection] = field(default_factory=set)
    interface_component: Component | None = None
    type_short_id: str = ""

    def add_connection(self, abstract_connection: AbstractConnection):
        self.abstract_connections.add(abstract_connection)

    def add_structure_components(self):
        structures: dict = json.load(open(structures_path))
        for component in structures[self.base_name]["Components"]:
            c_type = list(component.keys())[0]
            instance = get_instance_name(c_type, self.instance_n)
            component = Component(c_type=c_library.component_types[c_type], id=instance)
            self.structure.add(component)

            if structures[self.base_name]["InterfaceComponent"] == c_type:
                self.interface_component = component

    def add_structure_connections(self):
        structures: dict = json.load(open(structures_path))
        for component in structures[self.base_name]["Components"]:
            c_type = list(component.keys())[0]
            for comp, direction in component[c_type]["CONNECTIONS"].items():
                for comp_a in self.structure:
                    if comp_a.c_type.id == c_type:
                        for comp_b in self.structure:
                            if comp_b.c_type.id == comp:
                                new_connection = Connection.from_direction(
                                    component_a=comp_a, component_b=comp_b, direction=direction
                                )
                                self.connections.add(new_connection)

    @property
    def id(self) -> str:
        return get_instance_name(self.base_name, self.instance_n)

    @property
    def export(self) -> dict:
        return {
            self.id: {
                "position": self.grid_position,
                "connections": [e.component_b.id for e in self.abstract_connections],
            }
        }


@dataclass
class Fuselage(AbstractComponent):
    instance_n: int = 1

    def __post_init__(self):
        self.base_name = "Fuselage_str"
        self.add_structure_components()
        self.add_structure_connections()
        self.color = "red"
        self.type_short_id = "F"
        """TODO: add connections to components in structure"""

    def __hash__(self):
        return hash(self.id)


@dataclass
class Propeller(AbstractComponent):
    instance_n: int = 1

    def __post_init__(self):
        self.base_name = "Propeller_str_top"
        self.add_structure_components()
        self.add_structure_connections()
        self.color = "green"
        self.type_short_id = "P"

    def __hash__(self):
        return hash(self.id)


@dataclass
class BatteryController(AbstractComponent):
    instance_n: int = 1

    def __post_init__(self):
        self.base_name = "BatteryController"
        instance = get_instance_name("BatteryController", self.instance_n)
        lib_component = c_library.get_default_component("BatteryController")
        component = Component(
            c_type=c_library.component_types["BatteryController"], id=instance, library_component=lib_component
        )
        self.structure.add(component)
        self.interface_component = component
        self.type_short_id = "B"


@dataclass
class Wing(AbstractComponent):
    instance_n: int = 1

    def __post_init__(self):
        self.base_name = "Wing"
        self.color = "blue"
        instance = get_instance_name("Wing", self.instance_n)
        lib_component = c_library.get_default_component("Wing")
        component = Component(c_type=c_library.component_types["Wing"], id=instance, library_component=lib_component)
        component.parameters["Wing__TUBE_ROTATION"].value = 90.0
        self.structure.add(component)
        self.interface_component = component
        self.type_short_id = "W"

    def __hash__(self):
        return hash(self.id)


@dataclass
class Connector(AbstractComponent):
    instance_n: int = 1

    def __post_init__(self):
        self.base_name = "Connector"
        self.color = "gray"
        instance = get_instance_name("Hub4", self.instance_n)
        lib_component = c_library.get_default_component("Hub4")
        component = Component(c_type=c_library.component_types["Hub4"], id=instance, library_component=lib_component)
        self.structure.add(component)
        self.interface_component = component
        self.type_short_id = "C"

    def refine(self):
        for connection in self.abstract_connections:
            pass

    def __hash__(self):
        return hash(self.id)


@dataclass
class Tube(AbstractComponent):
    euclid_distance: int = 1
    instance_n: int = 1

    def __post_init__(self):
        self.base_name = "Tube"
        self.structure.add(Component(c_type=c_library.component_types["Tube"]))
        self.type_short_id = "T"

    def __hash__(self):
        return hash(self.id)


@dataclass
class Hub(AbstractComponent):
    instance_n: int = 1

    def __post_init__(self):
        self.base_name = "Hub"
        self.type_short_id = "H"

    def __hash__(self):
        return hash(self.id)
