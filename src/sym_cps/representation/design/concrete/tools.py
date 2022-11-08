from __future__ import annotations
from igraph import Graph, Vertex


def node_comparison(graph_1: Graph,
                    graph_2: Graph,
                    node_1: Vertex,
                    node_2: Vertex):

        c1 = graph_1.vs[node_1]["component"]
        c2 = graph_2.vs[node_2]["component"]
        equal = c1 == c2
        return equal


def edge_comparison(graph_1: Graph,
                    graph_2: Graph,
                    edge_1: int,
                    edge_2: int):

        c1 = graph_1.es[edge_1]["connection"]
        c2 = graph_2.es[edge_2]["connection"]
        return c1 == c2