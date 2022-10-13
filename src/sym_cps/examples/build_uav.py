import json

from sym_cps.grammar.topology import AbstractTopology
from sym_cps.representation.design.concrete import DConcrete
from sym_cps.representation.design.tools import generate_designs_info_files
from sym_cps.shared.library import designs
from sym_cps.shared.paths import ExportType
from sym_cps.tools.io import save_to_file

"""Generate topology.json from existing designs"""


def generate_topology(design_name: str):
    generate_designs_info_files(designs, design_name)


"""Generate design from topology.json"""

def analysis():
    quad = designs["TestQuad"][0]
    axe = designs["NewAxe"][0]

    print("TestQuad DP")
    for dp in quad.design_parameters.values():
        print(dp)

    print("NewAxe DP")
    for dp in axe.design_parameters.values():
        print(dp)

def modified_design():
    test_quad_original = designs["TestQuad"][0]

    test_quad_original.export(ExportType.JSON)
    test_quad_original.export(ExportType.PDF)
    test_quad_original.export(ExportType.DOT)
    topology_json_path = test_quad_original.export(ExportType.TOPOLOGY)
    test_quad_original.export(ExportType.TXT)
    # d_concrete_default.evaluate()

    # Changing Name
    f = open(topology_json_path)
    topology_json = json.load(f)
    topology_json["NAME"] = f"{topology_json['NAME']}MOD"
    new_file_path = save_to_file(
        str(json.dumps(topology_json)),
        file_name=f"topology_summary_mod.json",
        absolute_folder_path=topology_json_path.parent,
    )

    # Loading AbstractTopology form file
    abstract_topology = AbstractTopology.from_json(topology_json_path)
    abstract_topology.name += "Modified"
    new_file_path = save_to_file(
        abstract_topology.to_json(),
        file_name=f"topology_summary_modified.json",
        absolute_folder_path=topology_json_path.parent,
    )

    # Loading it ito a new design
    test_quad_from_topology = DConcrete.from_abstract_topology(abstract_topology)

    test_quad_from_topology.export(ExportType.JSON)
    test_quad_from_topology.export(ExportType.PDF)
    test_quad_from_topology.export(ExportType.DOT)
    test_quad_from_topology.export(ExportType.TOPOLOGY)
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
    # generate_topology("TestQuad")
    # topo_file = data_folder / "custom_designs" / "modified_test_quad.json"
    # generate_design(topo_file)
    modified_design()
    # analysis()
