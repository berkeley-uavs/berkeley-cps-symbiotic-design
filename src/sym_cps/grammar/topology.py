from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from aenum import Enum, auto


class AbstractionLevel(Enum):
    LOW = auto()


@dataclass
class AbstractTopology:
    name: str
    description: str
    connections: dict[str, dict[str, str]]
    parameters: dict[str, dict[str, float]]

    @classmethod
    def from_json(cls, topology_json_path: Path) -> AbstractTopology:
        f = open(topology_json_path)
        topo = json.load(f)
        name = topo["NAME"]
        description = topo["DESCRIPTION"]
        connections: dict[str, dict[str, str]] = {}
        parameters: dict[str, dict[str, str]] = {}
        if topo["ABSTRACTION"] == "LOW":
            for component_a, categories in topo["TOPOLOGY"].items():
                for category, infos in categories.items():
                    if category == "CONNECTIONS":
                        if component_a not in connections:
                            connections[component_a] = {}
                        for component_b, direction in infos.items():
                            connections[component_a][component_b] = direction
                    if category == "PARAMETERS":
                        if component_a not in parameters:
                            parameters[component_a] = {}
                        for param, value in infos.items():
                            parameters[component_a][param] = float(value)
        return cls(name, description, connections, parameters)

    def to_json(self, abstraction: AbstractionLevel = AbstractionLevel.LOW) -> str:
        if abstraction == AbstractionLevel.LOW:
            export: dict = {"NAME": self.name, "DESCRIPTION": "", "ABSTRACTION": "LOW", "TOPOLOGY": {}}
            for component_a, connections in self.connections.items():
                export["TOPOLOGY"][component_a] = {"CONNECTIONS": {}, "PARAMETERS": {}}
                """Parameters"""
                if component_a in self.parameters.keys():
                    for param, value in self.parameters[component_a].items():
                        export["TOPOLOGY"][component_a]["PARAMETERS"][param] = value
                """Connections"""
                for component_b, direction in connections.items():
                    print(export["TOPOLOGY"][component_a])
                    export["TOPOLOGY"][component_a]["CONNECTIONS"][component_b] = direction
            return str(json.dumps(export))

        if abstraction == AbstractionLevel.LOW:
            export: dict = {"NAME": self.name, "DESCRIPTION": "", "TOPOLOGY": {}}
            for component_a, connections in self.connections.items():
                export["TOPOLOGY"][component_a] = {"CONNECTIONS": {}, "PARAMETERS": {}}
                """Parameters"""
                if component_a in self.parameters.keys():
                    for param, value in self.parameters[component_a].items():
                        export["TOPOLOGY"][component_a]["PARAMETERS"][param] = value
                """Connections"""
                for component_b, direction in connections.items():
                    print(export["TOPOLOGY"][component_a])
                    export["TOPOLOGY"][component_a]["CONNECTIONS"][component_b] = direction
            return str(json.dumps(export))
