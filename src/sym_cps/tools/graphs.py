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
    graphs[0].write_pdf(pdf_file_path)