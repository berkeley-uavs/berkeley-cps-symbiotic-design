from __future__ import annotations

import json
import os
from enum import Enum, auto
from pathlib import Path

from sym_cps.representation.library import Library
from sym_cps.shared.objects import connections_map
from sym_cps.tools.io import save_to_file


class Direction(Enum):
    TOP = auto()
    BOTTOM = auto()
    LEFT = auto()
    INSIDE = auto()


def get_direction_from_components_and_connections(
        comp_type_a: str,
        comp_type_b: str,
        connector_id_a: str,
        connector_id_b: str) -> str:
    try:
        connections = connections_map[comp_type_a][comp_type_b]
    except:
        return "COMPONENT_ABSENT"
    for direction, (conn_a, conn_b) in connections.items():
        if conn_a == connector_id_a and conn_b == connector_id_b:
            return direction
    return "UNKNOWN"


def merge_connection_rules(folder: Path, library: Library):
    file_name_list = os.listdir(folder)

    abstract_connection_dict = {}

    concrete_connection_dict = {}
    default_connections = {}

    for name in file_name_list:
        if "connections.json" in name:
            file_path = folder / name
            with open(file_path) as json_file:
                data = json.load(json_file)
                for comp_a, components in data.items():
                    for comp_b, connections in components.items():
                        for connection in connections:
                            comp_a_conn, comp_b_conn, direction = tuple(connection)
                            type_a = library.components[comp_a].comp_type.id
                            type_b = library.components[comp_b].comp_type.id
                            if type_a not in default_connections.keys():
                                default_connections[type_a] = set()
                            default_connections[type_a].add(comp_a)
                            if comp_a not in concrete_connection_dict.keys():
                                concrete_connection_dict[comp_a] = {}
                            if comp_b not in concrete_connection_dict[comp_a].keys():
                                concrete_connection_dict[comp_a][comp_b] = {}
                            if type_a not in abstract_connection_dict.keys():
                                abstract_connection_dict[type_a] = {}
                            if type_b not in abstract_connection_dict[type_a].keys():
                                abstract_connection_dict[type_a][type_b] = {}
                            if direction != "":
                                if direction in concrete_connection_dict[comp_a][comp_b].keys():
                                    if (comp_a_conn, comp_b_conn) != concrete_connection_dict[comp_a][comp_b][
                                        direction
                                    ]:
                                        if "Hub" in f"{comp_a_conn}{comp_b_conn}":
                                            continue
                                        raise Exception(
                                            f"Contradicting Rules\n"
                                            f"{comp_a} -> {comp_b} ({direction})\n"
                                            f"{(comp_a_conn, comp_b_conn)}\n"
                                            f"{concrete_connection_dict[comp_a][comp_b][direction]}"
                                        )
                                if direction in abstract_connection_dict[type_a][type_b].keys():
                                    if (comp_a_conn, comp_b_conn) != abstract_connection_dict[type_a][type_b][
                                        direction
                                    ]:
                                        if "Hub" in comp_b_conn:
                                            continue
                                        raise Exception(
                                            f"Contradicting Rules\n"
                                            f"{type_a} -> {type_b} ({direction})\n"
                                            f"{comp_a} -> {comp_b} ({direction})\n"
                                            f"{(comp_a_conn, comp_b_conn)}\n"
                                            f"{abstract_connection_dict[comp_a][comp_b][direction]}"
                                        )
                                else:
                                    concrete_connection_dict[comp_a][comp_b][direction] = (comp_a_conn, comp_b_conn)
                                    abstract_connection_dict[type_a][type_b][direction] = (comp_a_conn, comp_b_conn)

    for key, values in default_connections.items():
        default_connections[key] = list(values)
    default_components = json.dumps(default_connections, indent=4)
    save_to_file(
        str(default_components),
        file_name=f"default_components.json",
        absolute_folder_path=connections_folder,
    )

    return concrete_connection_dict, abstract_connection_dict


def generalize_connection_rules(folder: Path):
    file_name_list = os.listdir(folder)

    for name in file_name_list:
        if name == "geometry_rules_abstract_mod.json":
            file_path = folder / name
            with open(file_path) as json_file:
                data = json.load(json_file)
                for comp_a, components in data.items():
                    for comp_b, connections in components.items():
                        for side, connectors in connections.items():
                            if side == "NONE":
                                if "NONE" in data[comp_b][comp_a].keys():
                                    if data[comp_b][comp_a]["NONE"][0] != connectors[1]:
                                        raise Exception("Conflict")
                                    if data[comp_b][comp_a]["NONE"][1] != connectors[0]:
                                        raise Exception("Conflict")
                                else:
                                    data[comp_b][comp_a]["NONE"] = [connectors[1], connectors[0]]

    connection_json = json.dumps(data, indent=4)
    save_to_file(
        str(connection_json),
        file_name=f"data_aug.json",
        absolute_folder_path=connections_folder,
    )


def export_connection_rules(connection_dict: dict):
    connection_json = json.dumps(connection_dict, indent=4)
    save_to_file(
        str(connection_json),
        file_name=f"geometry_rules.json",
        absolute_folder_path=connections_folder,
    )


def main():

    concrete_connection_dict, abstract_connection_dict = merge_connection_rules(connections_folder, c_library)
    connection_concrete_json = json.dumps(concrete_connection_dict, indent=4)
    save_to_file(
        str(connection_concrete_json),
        file_name=f"geometry_rules_concrete.json",
        absolute_folder_path=connections_folder,
    )
    connection_abstract_json = json.dumps(abstract_connection_dict, indent=4)
    save_to_file(
        str(connection_abstract_json),
        file_name=f"geometry_rules_abstract.json",
        absolute_folder_path=connections_folder,
    )

    print("\n\nMISSING CONNECTIONS")
    for comp_a, connections in abstract_connection_dict.items():
        for comp_b, conn in connections.items():
            if conn == {}:
                print(f"{comp_a} - {comp_b}")


if __name__ == "__main__":
    c_library, designs = parse_library_and_seed_designs()
    merge_connection_rules(connections_folder, c_library)
    # generalize_connection_rules(connections_folder)
