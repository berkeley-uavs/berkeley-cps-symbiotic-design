"""Generate design swri files for all designs in the library"""


from sym_cps.representation.tools.parsers.parse import parse_library_and_seed_designs
from sym_cps.shared.paths import ExportType

"""Loading Library and Seed Designs"""
c_library, designs = parse_library_and_seed_designs()


def generate_design_swri(design_name: str | None = None):
    if design_name is None:
        for _, design in designs.items():
            design_concrete = design[0]
            design_concrete.export(ExportType.JSON)
    else:
        design_concrete = designs[design_name][0]
        design_concrete.export(ExportType.JSON)


if __name__ == "__main__":
    generate_design_swri()
