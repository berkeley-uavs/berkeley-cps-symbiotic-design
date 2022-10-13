from sym_cps.representation.design.concrete import DConcrete
from sym_cps.representation.design.topology import DTopology
from sym_cps.representation.library import Library
from sym_cps.representation.tools.parsers.parse import parse_library_and_seed_designs
from sym_cps.tools.persistance import dump, load

c_library: Library = load("library.dat")
designs: dict[str, tuple[DConcrete, DTopology]] = load("designs.dat")
