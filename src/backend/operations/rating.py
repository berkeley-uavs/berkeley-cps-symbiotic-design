from sym_cps.optimizers.topo_opt import TopologyStrategy
from sym_cps.representation.design.topology import DTopology
from sym_cps.shared.paths import ExportType


class Rating:
    """Class that has all the useful functions to synthesis a design."""

    @staticmethod
    def generate_design(data: dict, session_id: str) -> str:
        """Create a design from a synthesis.

        Arguments:
            session_id: The id of the session where the design is saved.
            data: A dictionary that contains all the information of the design generation.

        Returns:
            The mealy machine that is/are the representation of the design.
        """
        full_name = data["name"]
        if data["strategy"] == "strategy_random":
            from backend.app import topo_opt
            d_topology: DTopology = topo_opt.generate_topology(
                name=full_name,
                strategy=TopologyStrategy.random_strategy
            )
            print("****D_TOPOLOGY****")
            print(d_topology)

            d_topology.export(ExportType.TXT)
            d_topology.export(ExportType.DOT)

            d_topology.export(ExportType.DOT)
            """TODO: SEND THE DOT (GRAPHVIZ) TO THE FRONT END AND VISUALIZE IT
            https://github.com/magjac/graphviz-visual-editor
            https://github.com/DomParfitt/graphviz-react
            https://www.npmjs.com/package/graphviz-react
            .... etc..
            """
            return "...GRAPHVIZ DOT GRAPH...."
