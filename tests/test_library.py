from sym_cps.representation.design.concrete import DConcrete
from sym_cps.representation.tools.parsers.parse import parse_library_and_seed_designs


def assert_check_dconcrete(d_concrete: DConcrete):
    assert isinstance(d_concrete, DConcrete)


def test_read_library():
    c_libary, designs = parse_library_and_seed_designs()

    for d_concrete in designs.values():
        assert_check_dconcrete(d_concrete)
