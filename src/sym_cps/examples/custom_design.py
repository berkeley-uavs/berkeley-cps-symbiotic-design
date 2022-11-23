from sym_cps.representation.design.concrete import DConcrete
from sym_cps.representation.design.human.topology import AbstractTopology
from sym_cps.shared.paths import data_folder

custom_design_file = data_folder / "custom_designs" / "cliff.json"


abstract_topology = AbstractTopology.from_json(custom_design_file)
dconcrete = DConcrete.from_abstract_topology(abstract_topology)
dconcrete.export_all()
