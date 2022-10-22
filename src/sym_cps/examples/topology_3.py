from sym_cps.shared.objects import ExportType
from tests.test_abastract_topology import assert_topology_from_and_to_json

"""Generate design from topology.json"""


if __name__ == "__main__":
    assert_topology_from_and_to_json(ExportType.TOPOLOGY_3)
