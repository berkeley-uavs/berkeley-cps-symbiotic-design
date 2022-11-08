import json
from copy import deepcopy

from sym_cps.shared.paths import connectors_components_path


def add_connection_with_direction(
        comp_type_a: str,
        comp_type_b: str,
        connector_id_a: str,
        connector_id_b: str,
        direction_a_to_b: str = "ANY",
        direction_b_to_a: str = "ANY"):
    connections_map: dict = json.load(open(connectors_components_path))
    if comp_type_a not in connections_map.keys():
        connections_map[comp_type_a] = {}
    if comp_type_b not in connections_map.keys():
        connections_map[comp_type_b] = {}
    connections_map[comp_type_a][comp_type_b] = {direction_b_to_a: [connector_id_a, connector_id_b]}
    connections_map[comp_type_b][comp_type_a] = {direction_a_to_b: [connector_id_b, connector_id_a]}

    print(f"Adding {comp_type_a}-{comp_type_b}-{connector_id_a}-{connector_id_b}-{direction_a_to_b}-{direction_b_to_a}")
    from sym_cps.tools.my_io import save_to_file
    save_to_file(connections_map, connectors_components_path)


def delete_key(key: str):
    connections_map: dict = json.load(open(connectors_components_path))
    new_dict = deepcopy(connections_map)
    for k1, v in connections_map.items():
        if k1 == key:
            for k2, v2 in v.items():
                if k1 in new_dict[k2].keys():
                    print(f"deleting {k2} - {k1}")
                    del new_dict[k2][k1]
            print(f"deleting {k1}")
            del new_dict[k1]

    from sym_cps.tools.my_io import save_to_file
    save_to_file(new_dict, connectors_components_path)


def delete_hubs():
    connections_map: dict = json.load(open(connectors_components_path))
    for k in connections_map:
        if "Hub" in k:
            delete_key(k)


def add_hubs():
    delete_hubs()
    for i in range(2, 7):
        comp_type_a = f"Hub{i}"
        comp_type_b = "Fuselage"
        add_connection_with_direction(
            comp_type_a=comp_type_a,
            comp_type_b=comp_type_b,
            connector_id_a=f"Hub{i}__Top_Connector",
            connector_id_b=f"Fuselage__BottomConnector",
            direction_b_to_a="TOP",
            direction_a_to_b="BOTTOM"
        )
        comp_type_b = "Orient"
        add_connection_with_direction(
            comp_type_a=comp_type_a,
            comp_type_b=comp_type_b,
            connector_id_a=f"Hub{i}__Orient_Connector",
            connector_id_b=f"Orient__ORIENTCONN",
        )
        comp_type_b = "Tube"
        add_connection_with_direction(
            comp_type_a=comp_type_a,
            comp_type_b=comp_type_b,
            connector_id_a=f"Hub{i}__Center_Connector",
            connector_id_b=f"Tube__BaseConnection",
            direction_b_to_a="TOP-CENTER",
            direction_a_to_b="CENTER-TOP"
        )
        add_connection_with_direction(
            comp_type_a=comp_type_a,
            comp_type_b=comp_type_b,
            connector_id_a=f"Hub{i}__Center_Connector",
            connector_id_b=f"Tube__EndConnection",
            direction_b_to_a="BOTTOM-CENTER",
            direction_a_to_b="CENTER-BOTTOM"
        )
        add_connection_with_direction(
            comp_type_a=comp_type_a,
            comp_type_b=comp_type_b,
            connector_id_a=f"Hub{i}__Top_Connector",
            connector_id_b=f"Tube__BaseConnection",
            direction_b_to_a="TOP-TOP",
            direction_a_to_b="TP{-TOP"
        )
        add_connection_with_direction(
            comp_type_a=comp_type_a,
            comp_type_b=comp_type_b,
            connector_id_a=f"Hub{i}__Top_Connector",
            connector_id_b=f"Tube__EndConnection",
            direction_b_to_a="BOTTOM-TOP",
            direction_a_to_b="TOP-BOTTOM"
        )
        for j in range(1, i+1):
            add_connection_with_direction(
                comp_type_a=comp_type_a,
                comp_type_b=comp_type_b,
                connector_id_a=f"Hub{i}__Side_Connector_{j}",
                connector_id_b=f"Tube__EndConnection",
                direction_b_to_a=f"TOP-SIDE{j}",
                direction_a_to_b=f"SIDE{j}-TOP"
            )
            add_connection_with_direction(
                comp_type_a=comp_type_a,
                comp_type_b=comp_type_b,
                connector_id_a=f"Hub{i}__Side_Connector_{j}",
                connector_id_b=f"Tube__BaseConnection",
                direction_b_to_a=f"BOTTOM-SIDE{j}",
                direction_a_to_b=f"SIDE{j}-BOTTOM"
            )


def add_sensors():
    add_connection_with_direction(
        comp_type_a="SensorCurrent",
        comp_type_b="Fuselage",
        connector_id_a="SensorCurrent__SensorConnector",
        connector_id_b="Fuselage__FloorConnector4"
    )
    add_connection_with_direction(
        comp_type_a="SensorRpmTemp",
        comp_type_b="Fuselage",
        connector_id_a="SensorRpmTemp__SensorConnector",
        connector_id_b="Fuselage__FloorConnector3"
    )
    add_connection_with_direction(
        comp_type_a="SensorVariometer",
        comp_type_b="Fuselage",
        connector_id_a="SensorVariometer__SensorConnector",
        connector_id_b="Fuselage__FloorConnector8"
    )
    add_connection_with_direction(
        comp_type_a="SensorAutopilot",
        comp_type_b="Fuselage",
        connector_id_a="SensorAutopilot__SensorConnector",
        connector_id_b="Fuselage__FloorConnector5"
    )
    add_connection_with_direction(
        comp_type_a="SensorVoltage",
        comp_type_b="Fuselage",
        connector_id_a="SensorVoltage__SensorConnector",
        connector_id_b="Fuselage__FloorConnector6"
    )
    add_connection_with_direction(
        comp_type_a="SensorGPS",
        comp_type_b="Fuselage",
        connector_id_a="SensorGPS__SensorConnector",
        connector_id_b="Fuselage__FloorConnector7"
    )


def fix_connectors_mapping():
    add_hubs()
    add_sensors()

if __name__ == '__main__':
    fix_connectors_mapping()