import os

import pydot
from igraph import Graph

from sym_cps.shared.paths import output_folder


def graph_to_pdf(graph: Graph, name: str, folder: str):
    if not os.path.exists(output_folder / folder):
        os.makedirs(output_folder / folder)
    pdf_file_path = output_folder / folder / f"{name}.pdf"
    dot_file_path = output_folder / folder / f"{name}.dot"
    graph.write_dot(f=str(dot_file_path))
    graphs = pydot.graph_from_dot_file(dot_file_path)
    # os.remove(dot_file_path)
    graphs[0].write_pdf(pdf_file_path)



def graph_to_dict(graph: Graph, name: str):
    components = list(graph.vs()["component"])
    connections = list(graph.es()["connection"])
    components_dict = {}
    connections_list = []
    for component in components:
        if component.c_type.id not in components_dict:
            components_dict[component.c_type.id] = {}
        if component.model not in components_dict[component.c_type.id].keys():
            components_dict[component.c_type.id][component.model] = {}
        if component.id not in components_dict[component.c_type.id][component.model].keys():
            components_dict[component.c_type.id][component.model][component.id] = component.params_values
    for connection in connections:
        connections_list.append(connection.summary)
    structure = {"NAME": name, "COMPONENTS": components_dict, "CONNECTIONS": connections_list}
    return structure
