from sym_cps.representation.tools.parsers.parse import parse_library_and_seed_designs
from sym_cps.tools.persistance import dump


def update_dat_files_library():
    """Loads library of components and seed designs and store them"""
    c_library, designs = parse_library_and_seed_designs()
    dump(c_library, "library.dat")
    dump(designs, "designs.dat")


def update_dat_designs():
    from sym_cps.shared.designs import designs
    dump(designs, "designs.dat")

def export_all_designs():
    from sym_cps.shared.designs import designs
    for (d_concrete, d_topology) in designs.values():
        d_concrete.export_all()
        d_topology.export_all()


def update_dat_files_and_export():
    """Loads library of components and seed designs and store them"""
    update_dat_files_library()
    export_all_designs()


if __name__ == "__main__":
    update_dat_files_and_export()
