from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sym_cps.representation.design.concrete.elements.component import Component
    from sym_cps.representation.library.elements.c_connector import CConnector


@dataclass(frozen=True)
class Connection:
    """Models the connection between two 'Component'.
    Each Connection is symmetric, i.e. Connection(A,B) = Connection(B,A)"""

    component_a: Component
    connector_a: CConnector
    component_b: Component
    connector_b: CConnector
    #brendan: make api to output connector_a and connect_b given component_a and component_b

    def __post_init__(self):
        """TODO: is connection legal?"""
        # call rules from src_cps.grammar


        legal_components = self.get_legal_components()
        type_a = self.component_a.c_type
        type_b = self.component_b.c_type

        if not (type_b in legal_components[type_a]["components"] or type_a in legal_components[type_b]["components"]):
            #do something it's broken
            return

        connector_name_a = self.connector_a.name
        connector_name_b = self.connector_b.name

        if not (connector_name_a in legal_components[type_a]["edge"] and connector_name_b in legal_components[type_b]["edge"]):
            #also broken
            return
        
        # legal_connectors = {
        #     "Prop_Connector": ["MOTOR_CONNECTOR_CS_IN"],
        #     "MOTOR_CONNECTOR_CS_IN": ["Prop_Connector"],
        #     "Base_Connector": ["TopConnector"],
        #     "MotorPower": ["MotorPower"],
        #     "TopConnector": ["Base_Connector"],
        #     "SideConnector": ["BaseConnection", "OffsetConnection1", "OffsetConnection2", "EndConnection"],
        #     "BottomConnector": ["BaseConnection", "EndConnection", "TopConnector", "BottomConnector"],
        #     "BaseConnection": ["SideConnector1-6", "CenterConnector", "SideConnector", "BottomConnector", "Wing_Tube_Connector"],
        #     "EndConnection": ["SideConnector1-6", "CenterConnector", "SideConnector", "BottomConnector", "Wing_Tube_Connector"],
        #     "OffsetConnection1": ["CenterConnector", "TopConnector", "BottomConnector", "SideConnector", "Wing_Tube_Connector"],
        #     "OffsetConnection2": ["CenterConnector", "TopConnector", "BottomConnector", "SideConnector", "Wing_Tube_Connector"],
        #     "Wing_Tube_Connector": ["BaseConnection", "OffsetConnection1", "OffsetConnection2", "EndConnection"],
        #     "PowerBus": ["BatteryPower"],
        #     "Sensor_Connector": ["FloorConnector1", "FloorConnector2", "FloorConnector3", "FloorConnector4", "FloorConnector5", "FloorConnector6", "FloorConnector7", "FloorConnector8"],
        #     "Case2HubConnector": ["BottomConnector", "TopConnector"],
        #     "CargoConnector": ["CargoConnector"],
        #     "CargoCase": ["CargoConnector"],

        # }
        


    @property
    def components_and_connectors(self) -> set[tuple[Component, CConnector]]:
        """Returns a set of two tuples, where each tuple is formed by a Component and a CConnector"""

        connections = set()
        connections.add((self.component_a, self.connector_a))
        connections.add((self.component_b, self.connector_b))
        return connections

    @property
    def components(self) -> tuple[Component, Component]:
        """Returns the two components connected"""

        return self.component_a, self.component_b

    @property
    def key(self) -> str:
        a1 = self.component_a.id
        a2 = self.connector_a.id
        b1 = self.component_b.id
        b2 = self.connector_b.id

        if (a1 + a2) >= (b1 + b2):
            return f"{a1}-{a2}-{b1}-{b2}"
        return f"{b1}-{b2}-{a1}-{a2}"

    def __eq__(self, other: object):
        if not isinstance(other, Connection):
            return NotImplementedError

        return self.key == other.key

    def __ne__(self, other: object):
        if not isinstance(other, Connection):
            return NotImplementedError

        return not self.__eq__(other)

    def __str__(self):

        s1 = f"FROM\n\tCOMPONENT\t{self.component_a.c_type.id} ({self.component_a.id})" \
             f"\n\tCONNECTOR\t{self.connector_a.name}\n"
        s2 = f"TO\n\tCOMPONENT\t{self.component_b.c_type.id} ({self.component_b.id})" \
             f"\n\tCONNECTOR\t{self.connector_b.name}\n"
        return f"{s1}{s2}"

    def __hash__(self):
        return abs(hash(self.key))
    
    def get_legal_components(self):
        """Returns legal connector and components for each component. """

        legal_components = {
            "Propeller": {
                "components": ["Motor"],
                "edge": ["MOTOR_CONNECTOR_CS_IN"]
                },
            "Motor": {
                "compenents": ["Proppeller", "Flange", "BatteryController"],
                "edge": ["Prop_Connector", "Base_Connector", "MotorPower"]          
                },
            "Flange": {
                "components": ["Motor", "Tube"],
                "edge": ["TopConnector", "SideConnector", "BottomConnector"]
                },
            "Tube": {
                "components": ["Hub", "Flange", "Wing_vert_hole", "Wing_horiz_hole", "Wing"],
                "edge": ["BaseConnection", "OffsetConnection1", "OffsetConnection2", "EndConnection"]
                },
            "Wing": {
                "components": ["Tube"],
                "edge": ["Wing_Tube_Connector"]
                },
            "CapsuleFuselage": {
                "components": ["Hub", "Battery", "Sensors"],
                "edge": ["BottomConnector", "FloorConnector1", "FloorConnector2", "FloorConnector3", "FloorConnector4", "FloorConnector5", "FloorConnector6", "FloorConnector7", "FloorConnector8"]
                },
            "Battery": {
                "components": ["CapsuleFuselage", "BatteryController"],
                "edge": ["Bottom_Connector", "PowerBus"]
                },
            "Sensors": {
                "components": ["CapsuleFuselage"],
                "edge": ["Sensor_Connector"]
                },
            "CargoCase": {
                "components": ["Hub", "Cargo"],
                "edge": ["Case2HubConnector", "CargoConnector"]
                },
            "Cargo": {
                "components": ["CargoCase"],
                "edge": ["CargoCase"]
                },
            "Hub": {
                "components": ["Tube", "CapsuleFuselage", "CargoCase", "Orient"],
                "edge": ["TopConnection", "BottomConnection", "CenterConnection", "OrientConnection", "SideConnector1", "SideConnector2", "SideConnector3", "SideConnector4", "SideConnector5", "SideConnector6"]
                },
            "Orient": {
                "components": ["Hub"],
                "edge": ["ORIENTCONN"]
                }
        }

        return legal_components
