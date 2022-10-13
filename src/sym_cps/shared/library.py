from sym_cps.representation.design.concrete import DConcrete
from sym_cps.representation.design.topology import DTopology
from sym_cps.representation.library import Library
from sym_cps.representation.tools.parsers.parse import parse_library_and_seed_designs
from sym_cps.tools.persistance import dump, load

c_library: Library = load("library.dat")
designs: dict[str, tuple[DConcrete, DTopology]] = load("designs.dat")


def update_dat_files():
    """Loads library of components and seed designs and store them"""
    c_library, designs = parse_library_and_seed_designs()
    dump(c_library, "library.dat")
    dump(designs, "designs.dat")


def export_all_designs():
    for (d_concrete, d_topology) in designs.values():
        d_concrete.export_all()
        d_topology.export_all()


if __name__ == "__main__":
    update_dat_files()
    export_all_designs()
