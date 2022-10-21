from sym_cps.representation.design.concrete import DConcrete
from sym_cps.representation.design.topology import DTopology
from sym_cps.tools.persistance import load

designs: dict[str, tuple[DConcrete, DTopology]] = load("designs.dat")
