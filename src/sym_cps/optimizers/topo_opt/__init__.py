import random
from dataclasses import dataclass
from enum import Enum, auto

from sym_cps.optimizers import Optimizer
from sym_cps.representation.design.topology import DTopology
from sym_cps.representation.library.elements.c_type import CType


class TopologyStrategy(Enum):
    random_strategy = auto()


@dataclass(frozen=True)
class TopologyOptimizer(Optimizer):
    def generate_topology(
        self,
        name: str,
        strategy: TopologyStrategy = TopologyStrategy.random_strategy,
        max_number_components: int = 10,
    ) -> DTopology:

        if strategy == TopologyStrategy.random_strategy:
            d_topology = DTopology(name=name)
            d_topology.add_node(c_type=random.choice(list(self.library.component_types.values())))

            while d_topology.n_nodes <= max_number_components:
                node_1 = d_topology.draw_random_node()
                node_1_type: CType = node_1["c_type"]

                if random.random() > 0.8:
                    node_2 = d_topology.draw_random_node()
                    node_2_type: CType = node_2["c_type"]
                    if node_1 != node_2 and node_2_type.id in node_1_type.compatible_with.keys():
                        d_topology.add_edge(node_1.index, node_2.index)

                else:
                    new_c_type = random.choice(list(node_1_type.compatible_with.keys()))
                    node_2 = d_topology.add_node(c_type=self.library.component_types[new_c_type])
                    d_topology.add_edge(node_1.index, node_2.index)
        else:
            raise NotImplementedError

        return d_topology
