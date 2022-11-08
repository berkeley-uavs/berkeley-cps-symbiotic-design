import json

from sym_cps.grammar.topology import AbstractTopology
from sym_cps.representation.design.concrete import DConcrete
from sym_cps.shared.designs import designs
from sym_cps.shared.objects import ExportType
from sym_cps.tools.io import save_to_file

"""Generate design from topology.json"""


def modified_design():
    test_quad_original = designs["TestQuad"][0]

    test_quad_original.export(ExportType.JSON)
    test_quad_original.export(ExportType.PDF)
    test_quad_original.export(ExportType.DOT)
    topology_json_path = test_quad_original.export(ExportType.TOPOLOGY_1)
    test_quad_original.export(ExportType.TXT)
    # d_concrete_default.evaluate()

    # Changing Name
    f = open(topology_json_path)
    topology_json = json.load(f)
    topology_json["NAME"] = f"{topology_json['NAME']}MOD"
    save_to_file(
        str(json.dumps(topology_json)),
        file_name=f"topology_summary_mod.json",
        absolute_path=topology_json_path.parent,
    )

    # Loading AbstractTopology form file
    abstract_topology = AbstractTopology.from_json(topology_json_path)
    abstract_topology.name += "Modified"
    save_to_file(
        abstract_topology.to_json(),
        file_name=f"topology_summary_modified.json",
        absolute_path=topology_json_path.parent,
    )

    # Loading it ito a new design
    test_quad_from_topology = DConcrete.from_abstract_topology(abstract_topology)

    test_quad_from_topology.export(ExportType.JSON)
    test_quad_from_topology.export(ExportType.PDF)
    test_quad_from_topology.export(ExportType.DOT)
    test_quad_from_topology.export(ExportType.TOPOLOGY_1)
    test_quad_from_topology.export(ExportType.TXT)

    print(len(test_quad_original.nodes))
    print(len(test_quad_from_topology.nodes))
    print(len(test_quad_original.edges))
    print(len(test_quad_from_topology.edges))

    connections_original = test_quad_original.connections
    print(f"{len(connections_original)} original connections")

    connections_mods = test_quad_from_topology.connections
    print(f"{len(connections_mods)} mod connections")

    test_quad_from_topology.evaluate()


if __name__ == "__main__":
    modified_design()
