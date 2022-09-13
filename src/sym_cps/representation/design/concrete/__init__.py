"""
Test Documentation
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

import igraph
from igraph import Graph, plot
from matplotlib import pyplot as plt
from sym_cps.representation.design.concrete.elements.component import Component
from sym_cps.representation.design.concrete.elements.connection import Connection
from sym_cps.representation.design.concrete.elements.design_parameters import DesignParameter
from sym_cps.representation.library.elements.c_type import CType
from sym_cps.representation.library.elements.library_component import LibraryComponent
from sym_cps.shared.paths import output_folder, ExportType, designs_folder
from sym_cps.tools.io import save_to_file
from sym_cps.tools.strings import tab


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
    design_parameters: dict[str, DesignParameter] = field(default_factory=dict)

    def __post_init__(self):
        self._graph = Graph()

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

    def add_node(self, component: Component) -> igraph.Vertex:
        return self.graph.add_vertex(
            instance=component.id,
            library_component=component.library_component,
            c_type=component.c_type,
            component=component,
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
        return None

    def select(
        self,
        library_component: LibraryComponent | None = None,
        component_type: CType | None = None,
    ) -> set[Component]:
        components = set()
        if library_component is not None:
            return set(
                self.graph.vs.select(library_component=library_component)["component"]
            )
        if component_type is not None:
            return set(self.graph.vs.select(component_type=component_type)["component"])
        return components

    @property
    def all_library_components_component_class(
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
        raise NotImplementedError

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

    def export(self, file_type: ExportType):
        absolute_folder = designs_folder / self.name

        if file_type == ExportType.TXT:
            save_to_file(
                str(self),
                file_name=f"DTopology",
                absolute_folder_path=absolute_folder,
            )
        elif file_type == ExportType.JSON:
            save_to_file(
                str(json.dumps(self.to_design_swri)),
                file_name=f"design_swri.json",
                absolute_folder_path=absolute_folder,
            )
        elif file_type == ExportType.DOT:
            self.graph.write_dot(f=str(absolute_folder / "concrete_graph.dot"))

        elif file_type == ExportType.PDF:
            if self.n_nodes > 0:
                layout = self.graph.layout("kk")
                """Adding labels to nodes"""
                self.graph.vs["label"] = self.graph.vs["c_type"]
                fig, ax = plt.subplots()
                plot(self.graph, layout=layout, target=ax)
                plt.savefig(absolute_folder / "concrete_graph.pdf")

        else:
            raise Exception("File type not supported")

        print(f"{file_type} file saved in {absolute_folder}")


    def draw(self, name):
        if self.n_nodes > 0:
            layout = self.graph.layout("kk")
            fig, ax = plt.subplots()
            plot(self.graph, layout=layout, target=ax)
            file_name_path = output_folder / "graphs" / name
            plt.savefig(f"{file_name_path}.pdf")

    def __eq__(self, other: object):
        pass

    def __ne__(self, other: object):

        if not isinstance(other, DConcrete):
            return NotImplementedError

        return not self.__eq__(other)

    def __str__(self):

        n_library_component_by_class = []
        for k, v in self.all_library_components_component_class.items():
            n_library_component_by_class.append(f"\t{k}: {len(v)}")
        n_library_component_by_class_str = "\n".join(n_library_component_by_class)

        components_list = []
        for (
            components_class,
            library_components,
        ) in self.all_library_components_component_class.items():
            components_list.append(tab(f"COMPONENT type: {components_class}"))
            for library_component in library_components:
                components_list.append(
                    tab(tab(f"LIBRARY COMPONENT: {library_component.id}"))
                )
                components = self.select(library_component=library_component)
                for component in components:
                    components_list.append(tab(tab(tab(f"COMPONENT: {component.id}"))))
                    components_list.append(tab(tab(tab(component))))
            components_list.append(
                "\n\t+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
            )

        components_str = "\n".join(components_list)

        s1 = (
            f"name: {self.name}\n"
            f"#_components: {len(self.components)}\n"
            f"#_connections: {len(self.connections)}\n"
            f"#_component_classes:\n{n_library_component_by_class_str}\n"
            f"components:\n{components_str}\n"
        )

        return s1
