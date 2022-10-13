import json

from sym_cps.representation.design.concrete import Connection, DConcrete
from sym_cps.shared.paths import ExportType, data_folder

"""Loading Library and Seed Designs"""

topo_file = data_folder / "reverse_engineering" / "test_quad_topology.json"

f = open(topo_file)
topo = json.load(f)

# Let us instantiate a DConcrete object
d_concrete = DConcrete(name=topo["NAME"])
components_to_nodes: dict = {}
for component_a, connections in topo["TOPOLOGY"].items():
    node_a_vertex = d_concrete.add_default_node(component_a, topo)
    for direction, component_b in connections.items():
        node_b_vertex = d_concrete.add_default_node(component_b, topo)
        connection = Connection.from_direction(
            component_a=node_a_vertex["component"], component_b=node_b_vertex["component"], direction=direction
        )
        d_concrete.connect(connection)

d_concrete.export(ExportType.JSON)
d_concrete.export(ExportType.PDF)
d_concrete.export(ExportType.DOT)
d_concrete.export(ExportType.TOPOLOGY)
d_concrete.export(ExportType.TXT)
