# from dataclasses import dataclass
#
# from sym_cps.grammar.elements import AbstractComponent, AbstractConnection, Connector, Fuselage, Propeller, Wing
#
#
# @dataclass
# class Structures:
#     elements: set[Structure]
#
#     def add_structure(self, structure: Structure):
#         self.elements.add(structure)
#
#     def learn_structures(self):
#         """TODO by Pier"""
#         pass
#
#
# @dataclass
# class Structure:
#     name: str
#     components: set[AbstractComponent]
#
#     @classmethod
#     def from_json(cls, structure_json_path: Path) -> Structure:
#         return Structure.from_dict(json.load(open(structure_json_path)))
#
#     @classmethod
#     def from_dict(cls, topo: dict) -> Structure:
#         """"TODO: takes dictionary and returns group of connected abstract components"""
#         name = topo["NAME"]
#         description = topo["DESCRIPTION"]
#         abstraction_level = topo["ABSTRACTION_LEVEL"]
#         connections: dict[str, dict[str, str]] = {}
#         parameters: dict[str, dict[str, str]] = {}
#
#         # for component_a, categories in topo["TOPOLOGY"].items():
#
