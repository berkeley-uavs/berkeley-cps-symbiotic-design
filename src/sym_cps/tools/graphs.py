import os

import pydot
from igraph import Graph

from sym_cps.shared.paths import output_folder


def graph_to_pdf(graph: Graph, name: str, folder: str):
    if not os.path.exists(output_folder / folder):
        os.makedirs(output_folder / folder)
    pdf_file_path = output_folder / folder / f"{name}.pdf"
    dot_file_path = output_folder / folder / "dot" / f"{name}.dot"
    if not os.path.exists(output_folder / folder / "dot"):
        os.makedirs(output_folder / folder / "dot")
    graph.write_dot(f=str(dot_file_path))
    graphs = pydot.graph_from_dot_file(dot_file_path)
    graphs[0].write_pdf(pdf_file_path)


def graph_to_dict(graph: Graph) -> tuple[str, dict]:
    components = sorted(list(graph.vs()["component"]), key=lambda x: x.c_type.id)
    connections = sorted(list(graph.es()["connection"]), key=lambda x: x.abstract_summary)
    components_dict = {}
    connections_list = []
    for component in components:
        if component.c_type.id not in components_dict:
            components_dict[component.c_type.id] = {}
        if component.model not in components_dict[component.c_type.id].keys():
            components_dict[component.c_type.id][component.model] = {}
        if component.id not in components_dict[component.c_type.id][component.model].keys():
            components_dict[component.c_type.id][component.model][component.id] = component.params_values_not_default
    added = []
    for connection in connections:
        if connection.key in added:
            continue
        connections_list.append(connection.abstract_summary)
        added.append(connection.key)
    components_dict = {key: value for key, value in sorted(components_dict.items())}
    structure = {"COMPONENTS": components_dict, "CONNECTIONS": connections_list}
    structure_key = "-".join(components_dict.keys())
    return structure_key, structure
