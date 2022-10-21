from sym_cps.examples.control import designs
from sym_cps.shared.objects import ExportType

# Loading DConcrete Object
test_quad_original = designs["TestQuad"][0]

# Exporting AbstractTopology to file
topology_json_path = test_quad_original.export(ExportType.TOPOLOGY_2)
