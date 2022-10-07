from __future__ import annotations

import json
import os
from enum import Enum, auto
from pathlib import Path

from sym_cps.representation.library import Library
from sym_cps.representation.tools.parsers.parse import parse_library_and_seed_designs
from sym_cps.shared.paths import data_folder
from sym_cps.tools.io import save_to_file


class Direction(Enum):
    TOP = auto()
    BOTTOM = auto()
    LEFT = auto()
    INSIDE = auto()


connections_folder = data_folder / "reverse_engineering"


def merge_connection_rules(folder: Path, library: Library):
    file_name_list = os.listdir(folder)

    abstract_connection_dict = {}
    concrete_connection_dict = {}

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
                                    if (comp_a_conn, comp_b_conn) != concrete_connection_dict[comp_a][comp_b][direction]:
                                        raise Exception(f"Contradicting Rules\n"
                                                        f"{comp_a} -> {comp_b} ({direction})\n"
                                                        f"{(comp_a_conn, comp_b_conn)}\n"
                                                        f"{concrete_connection_dict[comp_a][comp_b][direction]}")
                                if direction in abstract_connection_dict[type_a][type_b].keys():
                                    if (comp_a_conn, comp_b_conn) != abstract_connection_dict[type_a][type_b][direction]:
                                        raise Exception(f"Contradicting Rules\n"
                                                        f"{type_a} -> {type_b} ({direction})\n"
                                                        f"{comp_a} -> {comp_b} ({direction})\n"
                                                        f"{(comp_a_conn, comp_b_conn)}\n"
                                                        f"{abstract_connection_dict[comp_a][comp_b][direction]}")
                                else:
                                    concrete_connection_dict[comp_a][comp_b][direction] = (comp_a_conn, comp_b_conn)
                                    abstract_connection_dict[type_a][type_b][direction] = (comp_a_conn, comp_b_conn)

    return concrete_connection_dict, abstract_connection_dict


def export_connection_rules(connection_dict: dict):
    connection_json = json.dumps(connection_dict, indent=4)
    save_to_file(
        str(connection_json),
        file_name=f"geometry_rules.json",
        absolute_folder_path=connections_folder,
    )


if __name__ == '__main__':
    c_library, designs = parse_library_and_seed_designs()

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
