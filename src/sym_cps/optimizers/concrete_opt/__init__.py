"""
Test
"""
import random
from enum import Enum, auto

from sym_cps.optimizers import Optimizer
from sym_cps.representation.design.concrete import DConcrete
from sym_cps.representation.design.concrete.elements.component import Component
from sym_cps.representation.design.concrete.elements.connection import Connection
from sym_cps.representation.design.topology import DTopology
from sym_cps.representation.library.elements.c_connector import CConnector
from sym_cps.representation.tools.connectors import compatible_connectors


class ConcreteStrategy(Enum):
    """
    Test Class
    """

    random_strategy = auto()


class ConcreteOptimizer(Optimizer):
    def concretize_topology(
        self,
        d_topology: DTopology,
        strategy: ConcreteStrategy = ConcreteStrategy.random_strategy,
    ) -> DConcrete:

        d_concrete = DConcrete(name=d_topology.name)

        if strategy == ConcreteStrategy.random_strategy:
            for i in range(d_topology.n_nodes):
                """vertex index DTopology are the same in the DConcrete"""
                vertex = d_topology.get_vertex_by_id(i)
                c_type = vertex["c_type"]
                library_component = random.choice(list(self.library.components_in_type[c_type.id]))
                component = Component(id=str(i), library_component=library_component)
                d_concrete.add_node(component=component)
            print(d_concrete.graph)
            print(d_topology.graph)
            for edge in d_topology.edges:
                component_a: Component = d_concrete.get_vertex_by_id(edge.source)["component"]
                component_b: Component = d_concrete.get_vertex_by_id(edge.target)["component"]

                connectors_a = component_a.c_type.connectors.values()
                connectors_b = component_b.c_type.connectors.values()

                compatible_a_b_connectors: list[tuple[CConnector, CConnector]] = compatible_connectors(
                    connectors_a, connectors_b
                )

                connector_a, connector_b = random.choice(compatible_a_b_connectors)

                connection = Connection(
                    component_a=component_a,
                    connector_a=connector_a,
                    component_b=component_b,
                    connector_b=connector_b,
                )

                d_concrete.add_edge(node_id_a=edge.source, node_id_b=edge.target, connection=connection)
        else:
            raise NotImplementedError
        return d_concrete
