from typing import Iterable

from sym_cps.representation.library.elements.c_connector import CConnector


def compatible_connectors(
    connectors_a: Iterable[CConnector], connectors_b: Iterable[CConnector]
):
    compatible_a_b_connectors: list[tuple[CConnector, CConnector]] = []

    for connector_a in connectors_a:
        for connector_b in connectors_b:
            if connector_b in connector_a.compatible_with.values():
                compatible_a_b_connectors.append((connector_a, connector_b))

    return compatible_a_b_connectors
