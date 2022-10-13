import json

from sym_cps.representation.design.concrete import DConcrete
from sym_cps.representation.design.tools import generate_designs_info_files
from sym_cps.shared.library import designs
from sym_cps.shared.paths import ExportType
from sym_cps.tools.io import save_to_file

"""Generate topology.json from existing designs"""


def generate_topology(design_name: str):
    generate_designs_info_files(designs, design_name)


"""Generate design from topology.json"""


def modified_design():
    d_concrete_default = designs["TestQuad"][0]

    d_concrete_default.export(ExportType.JSON)
    d_concrete_default.export(ExportType.PDF)
    d_concrete_default.export(ExportType.DOT)
    topology_json_path = d_concrete_default.export(ExportType.TOPOLOGY)
    d_concrete_default.export(ExportType.TXT)

    # Changing Name
    f = open(topology_json_path)
    topology_json = json.load(f)
    topology_json["NAME"] = f"{topology_json['NAME']}MOD"
    new_file_path = save_to_file(
        str(json.dumps(topology_json)),
        file_name=f"topology_summary_mod.json",
        absolute_folder_path=topology_json_path.parent,
    )

    # Loading it ito a new design
    d_concrete = DConcrete.from_topology_summary(new_file_path)

    d_concrete.export(ExportType.JSON)
    d_concrete.export(ExportType.PDF)
    d_concrete.export(ExportType.DOT)
    d_concrete.export(ExportType.TOPOLOGY)
    d_concrete.export(ExportType.TXT)

    print(len(d_concrete.nodes))
    print(len(d_concrete_default.nodes))
    print(len(d_concrete.edges))
    print(len(d_concrete_default.edges))

    connections_original = d_concrete_default.connections
    print(f"{len(connections_original)} original connections")
    connections_mods = d_concrete.connections
    print(f"{len(connections_mods)} mod connections")

    for orig_conn in connections_original:
        found = False
        for new_conn in connections_mods:
            if new_conn.is_similar(orig_conn):
                found = True
        if found == False:
            print("NOT FOUND")
            print(orig_conn)

    # print(f"{len(missing_connections)} missing connections")

    d_concrete.evaluate()


if __name__ == "__main__":
    # generate_topology("TestQuad")
    # topo_file = data_folder / "custom_designs" / "modified_test_quad.json"
    # generate_design(topo_file)
    modified_design()
