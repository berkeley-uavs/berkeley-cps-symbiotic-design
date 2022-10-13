"""
Test Documentation
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

import igraph
import matplotlib
from igraph import Graph, plot
from sym_cps.evaluation import evaluate_design
from sym_cps.grammar.topology import AbstractTopology, AbstractionLevel
from sym_cps.representation.design.concrete.elements.parameter import Parameter
from sym_cps.representation.tools.dictionaries import number_of_instances_in_dict

matplotlib.use("TkAgg")
from matplotlib import pyplot as plt

from sym_cps.grammar.tools import get_direction_from_components_and_connections
from sym_cps.representation.design.concrete.elements.component import Component
from sym_cps.representation.design.concrete.elements.connection import Connection
from sym_cps.representation.design.concrete.elements.design_parameters import DesignParameter
from sym_cps.representation.library.elements.c_type import CType
from sym_cps.representation.library.elements.library_component import LibraryComponent
from sym_cps.shared.paths import ExportType, designs_folder
from sym_cps.tools.io import save_to_file
from sym_cps.tools.strings import repr_dictionary, tab


@dataclass
class DConcrete:
    """
    A class representing a Concrete Design

    ...

    Attributes
    ----------
    name : str
        name of the design
    design_parameters : dict[str, DesignParameter]
        design parameters
    """

    name: str
    description: str = ""
    design_parameters: dict[str, DesignParameter] = field(default_factory=dict)
    comp_id_to_node: dict[str, igraph.Vertex] = field(default_factory=dict)

    def __post_init__(self):
        self._graph = Graph(directed=True)
        self.description = "empty_description"

    @classmethod
    def from_abstract_topology(cls, topo: AbstractTopology):

        d_concrete = cls(name=topo.name)
        for component_a, connections in topo.connections.items():
            node_a_vertex = d_concrete.add_default_node(component_a)
            """Parameters"""
            if component_a in topo.parameters.keys():
                node_a_vertex["component"].update_parameters(topo.parameters[component_a])
            """Connections"""
            for component_b, direction in connections.items():
                node_b_vertex = d_concrete.add_default_node(component_b)
                connection = Connection.from_direction(
                    component_a=node_a_vertex["component"],
                    component_b=node_b_vertex["component"],
                    direction=direction,
                )
                d_concrete.connect(connection)

        return d_concrete

    @property
    def graph(self) -> Graph:
        return self._graph

    @property
    def nodes(self) -> list[igraph.Vertex]:
        return list(self.graph.vs)

    @property
    def edges(self) -> list[igraph.Edge]:
        return list(self.graph.es)

    def get_vertex_by_id(self, vid: int) -> igraph.Vertex:
        return self.graph.vs[vid]

    @property
    def n_nodes(self) -> int:
        return len(self.graph.vs)

    @property
    def n_edges(self) -> int:
        return len(self.graph.es)

    def export_parameters(self) -> dict[str, dict[str, Parameter]]:
        pass

    def add_default_node(self, abstract_component_id: str) -> igraph.Vertex:
        if abstract_component_id in self.comp_id_to_node.keys():
            return self.comp_id_to_node[abstract_component_id]
        id_split = abstract_component_id.split("_")
        try:
            if id_split[-2] == "instance":
                node_type_a = "_".join(id_split[:-2])
            else:
                node_type_a = abstract_component_id
        except:
            node_type_a = abstract_component_id

        from sym_cps.shared.library import c_library

        lib_comp_a = c_library.get_default_component(node_type_a)
        instance_a = Component(id=abstract_component_id, library_component=lib_comp_a)
        self.comp_id_to_node[abstract_component_id] = self.add_node(instance_a)
        return self.comp_id_to_node[abstract_component_id]

    def add_node(self, component: Component) -> igraph.Vertex:
        return self.graph.add_vertex(
            instance=component.id,
            library_component=component.library_component,
            c_type=component.c_type,
            component=component,
            label=f"{component.library_component.id}",
        )

    def remove_node(self):
        """TODO"""
        raise NotImplementedError

    def add_edge(self, node_id_a: int, node_id_b: int, connection: Connection):
        self.graph.add_edge(source=node_id_a, target=node_id_b, connection=connection)

    def connect(self, connection: Connection):
        a = self.get_node_by_instance(connection.component_a.id).index
        b = self.get_node_by_instance(connection.component_b.id).index
        self.add_edge(a, b, connection)
        # print(f"Edge: {a}: {connection.component_a.id} -> {b}: {connection.component_b.id}")

    def remove_edge(self):
        """TODO. Tip: self.graph.delete_edges"""
        raise NotImplementedError

    def disconnect(self, connection: Connection):
        """TODO. Might want to remove a Connection, retrieve the node_id from the Connection"""
        raise NotImplementedError

    @property
    def components(self) -> set[Component | None]:
        if self.n_nodes > 0:
            return set(self.graph.vs()["component"])
        return set()

    @property
    def parameters(self) -> set[Parameter | None]:
        parameters = set()
        for component in self.components:
            for para_id, parameter in component.parameters.items():
                parameters.add(parameter)
        return parameters

    @property
    def connections(self) -> set[Connection | None]:
        if self.n_nodes > 0:
            if self.n_edges > 0:
                return set(self.graph.es()["connection"])
        return set()

    def get_node_by_instance(self, instance: str) -> igraph.Vertex | None:
        if self.n_nodes > 0:
            nodes = self.graph.vs.select(instance=instance)
            if len(nodes) == 1:
                return nodes[0]
        return None

    def get_instance(self, instance: str) -> Component | None:
        if self.n_nodes > 0:
            nodes = self.graph.vs.select(instance=instance)
            if len(nodes) == 1:
                return nodes["component"][0]
        print(f"{instance} NOT FOUND")
        for v in self.graph.vs:
            print(v["instance"])
        raise Exception

    def select(
        self,
        library_component: LibraryComponent | None = None,
        component_type: CType | None = None,
    ) -> set[Component]:
        components = set()
        if library_component is not None:
            return set(self.graph.vs.select(library_component=library_component)["component"])
        if component_type is not None:
            return set(self.graph.vs.select(component_type=component_type)["component"])
        return components

    @property
    def all_library_components_in_type(
        self,
    ) -> dict[CType, set[LibraryComponent]]:
        """Returns all LibraryComponent for each Component class in the design"""
        comp_types_n: dict[CType, set[LibraryComponent]] = {}
        for component in self.components:
            if component.c_type in comp_types_n.keys():
                comp_types_n[component.c_type].add(component.library_component)
            else:
                comp_types_n[component.c_type] = {component.library_component}
        return comp_types_n

    @property
    def all_components_by_library_components(
        self,
    ) -> dict[LibraryComponent, set[Component]]:
        """Returns all Components for each LibraryComponent in the design"""
        comp_types_n: dict[LibraryComponent, set[Component]] = {}
        for component in self.components:
            if component.library_component in comp_types_n.keys():
                comp_types_n[component.library_component].add(component)
            else:
                comp_types_n[component.library_component] = {component}
        return comp_types_n

    def validate(self):
        """Validates the Parameters of the Design"""
        raise NotImplementedError

    def evaluate(self):
        """Sends the Design for evaluation"""
        json_path = self.export(ExportType.JSON)
        evaluate_design(design_json_path=json_path, metadata={"extra_info": "full evaluation example"}, timeout=800)

    def evaluation(self, evaluation_results_json: str):
        """Parse and update the evaluation of the Design"""
        raise NotImplementedError

    def export_to_cad(self):
        """Generates a CAD representation of the Design"""
        raise NotImplementedError

    @property
    def to_design_swri(self) -> dict[str, str]:
        """Generate design_swri.json format file from a concrete design
        design: the concrete design exporting to design_swri.json file
        output_path: file path for the export file.
        """
        design_swri_data = {}

        """ Storing the design name"""
        design_swri_data["name"] = self.name

        """Storing parameters"""
        data_parameters: list = []

        for component in self.components:
            for parameter_id, parameter in component.parameters.items():
                data_parameters.append(
                    {
                        "parameter_name": f"{component.id}_{parameter.c_parameter.name}",
                        "value": str(int(parameter.value)),
                        "component_properties": [
                            {
                                "component_name": component.id,
                                "component_property": parameter.c_parameter.name,
                            }
                        ],
                    }
                )
        design_swri_data["parameters"] = data_parameters

        """Storing components"""
        data_components: list[dict[str, str]] = []
        for component in self.components:
            data_components.append(
                {
                    "component_instance": component.id,
                    "component_type": component.c_type.id,
                    "component_choice": component.model,
                }
            )
        design_swri_data["components"] = data_components

        """Storing connections"""
        data_connections: list[dict[str, str]] = []
        for connection in self.connections:
            data_connections.append(
                {
                    "from_ci": connection.component_a.id,
                    "from_conn": connection.connector_a.name,
                    "to_ci": connection.component_b.id,
                    "to_conn": connection.connector_b.name,
                }
            )
            data_connections.append(
                {
                    "from_ci": connection.component_b.id,
                    "from_conn": connection.connector_b.name,
                    "to_ci": connection.component_a.id,
                    "to_conn": connection.connector_a.name,
                }
            )
        design_swri_data["connections"] = data_connections

        return design_swri_data

    def to_abstract_topology(self) -> AbstractTopology:
        name = self.name
        description = self.description
        connections: dict[str, dict[str, str]] = {}
        parameters: dict[str, dict[str, float]] = {}

        """Connections"""
        for edge in self.edges:
            node_id_s = self._graph.vs[edge.source]['instance']
            node_id_t = self._graph.vs[edge.target]['instance']
            direction = edge["connection"].direction_b_respect_to_a()
            if node_id_s not in connections:
                connections[node_id_s] = {}
            connections[node_id_s][node_id_t] = direction

        """Parameters"""
        for node in self.nodes:
            node_id = node["instance"]
            if node_id not in connections.keys():
                """Adding nodes with no connections"""
                connections[node_id] = {}
            if node_id not in parameters.keys():
                """Adding nodes with no connections"""
                parameters[node_id] = {}
            for parameter_id, parameter in node["component"].parameters.items():
                parameters[node_id][parameter_id] = float(parameter.value)

        return AbstractTopology(name, description, connections, parameters)

    def export(self, file_type: ExportType) -> Path:
        absolute_folder = designs_folder / self.name

        if file_type == ExportType.TXT:
            return save_to_file(
                str(self),
                file_name=f"DConcrete",
                absolute_folder_path=absolute_folder,
            )
        elif file_type == ExportType.TOPOLOGY:
            ab_topo = self.to_abstract_topology()
            return save_to_file(
                ab_topo.to_json(AbstractionLevel.LOW),
                file_name=f"topology_summary.json",
                absolute_folder_path=absolute_folder,
            )

        elif file_type == ExportType.JSON:
            return save_to_file(
                str(json.dumps(self.to_design_swri)),
                file_name=f"design_swri.json",
                absolute_folder_path=absolute_folder,
            )
        elif file_type == ExportType.DOT:
            if not os.path.exists(absolute_folder):
                os.makedirs(absolute_folder)
            file_path = absolute_folder / "concrete_graph.dot"
            self.graph.write_dot(f=str(file_path))

        elif file_type == ExportType.PDF:
            file_path = absolute_folder / "concrete_graph.pdf"
            if self.n_nodes > 0:
                layout = self.graph.layout("kk")
                """Adding labels to nodes"""
                fig, ax = plt.subplots()
                plot(self.graph, scale=50, vertex_size=0.2, edge_width=[1, 1], layout=layout, target=ax)
                plt.savefig(file_path)
        else:
            raise Exception("File type not supported")

        print(f"{file_type} file saved in {absolute_folder}")
        return file_path

    def export_all(self):
        self.export(ExportType.DOT)
        self.export(ExportType.PDF)
        self.export(ExportType.TXT)
        self.export(ExportType.TOPOLOGY)
        self.export(ExportType.JSON)

    def __eq__(self, other: object):
        pass

    def __ne__(self, other: object):

        if not isinstance(other, DConcrete):
            return NotImplementedError

        return not self.__eq__(other)

    def generate_connections_json(self):

        connection_dict = {}
        for (
            components_class,
            library_components,
        ) in self.all_library_components_in_type.items():
            for library_component in library_components:
                connection_dict[library_component.id] = {}
                components = self.select(library_component=library_component)
                for component in components:
                    for connection in self.connections:
                        direction = get_direction_from_components_and_connections(
                            connection.component_a.c_type.id,
                            connection.component_b.c_type.id,
                            connection.connector_a.id,
                            connection.connector_b.id,
                        )
                        if component.id == connection.component_a.id:
                            if (
                                connection.component_b.library_component.id
                                in connection_dict[library_component.id].keys()
                            ):
                                connection_dict[library_component.id][
                                    connection.component_b.library_component.id
                                ].append((connection.connector_a.id, connection.connector_b.id, direction))
                            else:
                                connection_dict[library_component.id][connection.component_b.library_component.id] = [
                                    (connection.connector_a.id, connection.connector_b.id, direction)
                                ]

                        if component.id == connection.component_b.id:
                            if (
                                connection.component_a.library_component.id
                                in connection_dict[library_component.id].keys()
                            ):
                                connection_dict[library_component.id][
                                    connection.component_a.library_component.id
                                ].append((connection.connector_b.id, connection.connector_a.id, direction))
                            else:
                                connection_dict[library_component.id][connection.component_a.library_component.id] = [
                                    (connection.connector_b.id, connection.connector_a.id, direction)
                                ]

        connection_json = json.dumps(connection_dict, indent=4)
        return connection_json

    def get_neighbours_of(self, node: igraph.Vertex) -> list[igraph.Vertex]:
        neighbors = self._graph.neighbors(node.index)
        neighbors = set(neighbors)
        neighbors_vertices = []
        for n in neighbors:
            neighbors_vertices.append(self._graph.vs.select(n)[0])
        return neighbors_vertices

    def get_edges_from(self, node: igraph.Vertex) -> igraph.EdgeSeq:
        return self._graph.es.select(_source=node.index)

    def get_edges_to(self, node: igraph.Vertex) -> igraph.EdgeSeq:
        return self._graph.es.select(_target=node.index)

    # def get_edges_of(self, node: igraph.Vertex) -> set(igraph.Edge):
    #     edges = set()
    #     edges |= set(self._graph.es.select(_source=[node.index]))
    #     edges |= set(self._graph.es.select(_target=[node.index]))
    #     return edges

    def __str__(self):

        ret = "TOPOLOGY SUMMARY\n\n"
        connections_map: dict = {}
        ret += "<VERTEX_ID> - <COMPONENT_INSTANCE>::<LIBRARY_COMPONENT>::<COMPONENT_TYPE>\n\n"
        for node in self.nodes:
            node_id = f"{node.index} - {node['instance']}::{node['label']}::{node['c_type']}"
            connections_map[node_id] = []
            print(f"SOURCE NODE:\t{node['instance']}")
            for edge in self.get_edges_from(node):
                print(edge["connection"])
                t_node = self._graph.vs[edge.target]
                dir = edge["connection"].direction_b_respect_to_a()
                c_a = edge["connection"].component_a.id
                c_b = edge["connection"].component_b.id
                conn_a = edge["connection"].connector_a.id
                conn_b = edge["connection"].connector_b.id
                t_node_id = (
                    f"{dir} -- {t_node.index} - {t_node['instance']}::{t_node['label']}::{t_node['c_type']}\n"
                    f"\t\t{c_a}:{conn_a} -> {c_b}:{conn_b}"
                )
                connections_map[node_id].append(t_node_id)
            print("\n\n")
        ret += repr_dictionary(connections_map)
        ret += "\n\n"
        ret += str(self._graph)

        n_library_component_by_class = []
        for k, v in self.all_library_components_in_type.items():
            n_library_component_by_class.append(f"\t{k}: {len(v)}")
        n_library_component_by_class_str = "\n".join(n_library_component_by_class)

        components_list = []
        # connections_by_components = {}

        for (
            components_class,
            library_components,
        ) in self.all_library_components_in_type.items():
            components_list.append(tab(f"COMPONENT type: {components_class}"))
            for library_component in library_components:
                components_list.append(tab(tab(f"LIBRARY COMPONENT: {library_component.id}")))
                components = self.select(library_component=library_component)
                for component in components:
                    components_list.append(tab(tab(tab(f"COMPONENT: {component.id}"))))
                    components_list.append(tab(tab(tab(tab(f"CONNECTIONS:")))))
                    for connection in self.connections:
                        if component.id == connection.component_a.id:
                            components_list.append(
                                tab(
                                    tab(
                                        tab(
                                            tab(
                                                tab(
                                                    f"{connection.component_a.library_component.id} :: {connection.connector_a.id} <<->> {connection.connector_b.id} :: {connection.component_b.id} ({connection.component_b.library_component.id})"
                                                )
                                            )
                                        )
                                    )
                                )
                            )
                        if component.id == connection.component_b.id:
                            components_list.append(
                                tab(
                                    tab(
                                        tab(
                                            tab(
                                                tab(
                                                    f"{connection.component_b.library_component.id} :: {connection.connector_b.id} <<->> {connection.connector_a.id} :: {connection.component_a.id} ({connection.component_a.library_component.id})"
                                                )
                                            )
                                        )
                                    )
                                )
                            )

                    # components_list.append(tab(tab(tab(f"COMPONENT: {component}"))))
                    # components_list.append(tab(tab(tab(component))))
            components_list.append("\n\t+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

        connection_list = []
        for connection in self.connections:
            connection_list.append(str(connection))

        components_str = "\n".join(components_list)
        connection_str = "\n".join(connection_list)

        s1 = (
            f"\n\nname: {self.name}\n"
            f"#_components: {len(self.components)}\n"
            f"#_connections: {len(self.connections)}\n"
            f"#_component_classes:\n{n_library_component_by_class_str}\n"
            f"\n\nconnections:\n{connection_str}\n"
            f"\n\ncomponents:\n{components_str}\n"
        )

        return ret + s1
