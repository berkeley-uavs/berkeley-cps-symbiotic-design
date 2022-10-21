from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from aenum import Enum, auto

from sym_cps.shared.library import c_library
from sym_cps.shared.objects import default_parameters
from sym_cps.tools.strings import get_component_type_from_instance_name


class AbstractionFeatures(Enum):
    AVOID_REDUNDANT_CONNECTIONS = auto()
    USE_DEFAULT_PARAMETERS = auto()


abstraction_levels_features = {
    1: {},
    2: {AbstractionFeatures.USE_DEFAULT_PARAMETERS},
    3: {AbstractionFeatures.AVOID_REDUNDANT_CONNECTIONS},
    4: {AbstractionFeatures.AVOID_REDUNDANT_CONNECTIONS, AbstractionFeatures.USE_DEFAULT_PARAMETERS},
}


@dataclass
class AbstractTopology:
    name: str
    description: str
    connections: dict[str, dict[str, str]]
    parameters: dict[str, dict[str, float]]

    @classmethod
    def from_json(cls, topology_json_path: Path) -> AbstractTopology:
        topo = json.load(open(topology_json_path))
        name = topo["NAME"]
        description = topo["DESCRIPTION"]
        abstraction_level = topo["ABSTRACTION_LEVEL"]
        connections: dict[str, dict[str, str]] = {}
        parameters: dict[str, dict[str, str]] = {}
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
                    if AbstractionFeatures.USE_DEFAULT_PARAMETERS in abstraction_levels_features[abstraction_level]:
                        c_type: str = get_component_type_from_instance_name(component_a)
                        for parameter in c_library.component_types[c_type].parameters.values():
                            if parameter.id in default_parameters.keys():
                                parameters[component_a][parameter.id] = float(default_parameters[parameter.id])
                    for param, value in infos.items():
                        parameters[component_a][param] = float(value)
        return cls(name, description, connections, parameters)

    def to_json(self, abstraction_level: int) -> str:
        export: dict = {"NAME": self.name, "DESCRIPTION": "", "ABSTRACTION_LEVEL": abstraction_level, "TOPOLOGY": {}}

        for component_a, connections in self.connections.items():
            export["TOPOLOGY"][component_a] = {"CONNECTIONS": {}, "PARAMETERS": {}}
            """Parameters"""
            if component_a in self.parameters.keys():
                for param, value in self.parameters[component_a].items():
                    if AbstractionFeatures.USE_DEFAULT_PARAMETERS in abstraction_levels_features[abstraction_level]:
                        if param in default_parameters.keys():
                            continue
                    export["TOPOLOGY"][component_a]["PARAMETERS"][param] = value
            """Connections"""
            for component_b, direction in connections.items():
                print(export["TOPOLOGY"][component_a])
                export["TOPOLOGY"][component_a]["CONNECTIONS"][component_b] = direction
        return str(json.dumps(export))
