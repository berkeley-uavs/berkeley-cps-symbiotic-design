import json

from sym_cps.shared.paths import connectors_components_path
from sym_cps.tools.my_io import save_to_file


def add_connection_with_direction(
    comp_type_a: str,
    comp_type_b: str,
    connector_id_a: str,
    connector_id_b: str,
    direction_a_to_b: str = "ANY",
    direction_b_to_a: str = "ANY",
):
    connections_map: dict = json.load(open(connectors_components_path))
    connections_map[comp_type_a] = {}
    connections_map[comp_type_b] = {}
    connections_map[comp_type_a][comp_type_b] = {direction_b_to_a: [connector_id_a, connector_id_b]}
    connections_map[comp_type_b][comp_type_a] = {direction_a_to_b: [connector_id_b, connector_id_a]}

    save_to_file(connections_map, connectors_components_path)


if __name__ == "__main__":
    add_connection_with_direction(
        comp_type_a="SensorCurrent",
        comp_type_b="Fuselage",
        connector_id_a="SensorCurrent__SensorConnector",
        connector_id_b="Fuselage__FloorConnector4",
    )
    add_connection_with_direction(
        comp_type_a="SensorRpmTemp",
        comp_type_b="Fuselage",
        connector_id_a="SensorRpmTemp__SensorConnector",
        connector_id_b="Fuselage__FloorConnector3",
    )
    add_connection_with_direction(
        comp_type_a="SensorVariometer",
        comp_type_b="Fuselage",
        connector_id_a="SensorVariometer__SensorConnector",
        connector_id_b="Fuselage__FloorConnector8",
    )
    add_connection_with_direction(
        comp_type_a="SensorAutopilot",
        comp_type_b="Fuselage",
        connector_id_a="SensorAutopilot__SensorConnector",
        connector_id_b="Fuselage__FloorConnector5",
    )
    add_connection_with_direction(
        comp_type_a="SensorVoltage",
        comp_type_b="Fuselage",
        connector_id_a="SensorVoltage__SensorConnector",
        connector_id_b="Fuselage__FloorConnector6",
    )
    add_connection_with_direction(
        comp_type_a="SensorGPS",
        comp_type_b="Fuselage",
        connector_id_a="SensorGPS__SensorConnector",
        connector_id_b="Fuselage__FloorConnector7",
    )
