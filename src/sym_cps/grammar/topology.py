from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from sym_cps.shared.paths import data_folder
from sym_cps.representation.library import LibraryComponent

from aenum import Enum, auto
from sym_cps.shared.library import c_library

class AbstractionLevel(Enum):
    LOW = auto()
    USE_DEFAULT = auto()


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

        if topo["ABSTRACTION"] == "USE_DEFAULT":
            """Load learned parameters json"""
            learned_param_path = data_folder / "reverse_engineering" / "analysis" / "learned_parameters.json"
            f = open(learned_param_path)
            default = json.load(f)
            default = default['PARAMETERS']['ALL']['SHARED']['VALUES']
            """CONNECTIONS are same as abstraction == "LOW" """
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

                        """Load parameters for particular component from c_library"""
                        params_dict = c_library.components[component_a].parameters() 

                        """all_params hold all the parameters for component_a"""
                        all_params = list(params_dict.keys())

                        """If parameter value is specified in topology json => remove it from list of all _params and assign value in parameters"""
                        for param, value in infos.items():
                            parameters[component_a][param] = float(value)
                            all_params.remove(param)
                        
                        """For all parameters not specified in topology json assign value from default json"""
                        for p in all_params:
                            if p in default.keys():
                                parameters[component_a][p] = float(default[p])

                        

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

        if abstraction == AbstractionLevel.USE_DEFAULT:
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
