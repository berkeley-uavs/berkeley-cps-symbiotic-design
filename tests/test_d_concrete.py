from copy import deepcopy

from sym_cps.shared.designs import designs


def assert_different_object_after_parameter_change():
    test_quad_original = designs["TestQuad"][0]
    test_quad_original2 = deepcopy(designs["TestQuad"][0])
    test_quad_original2.get_instance("Propeller_instance_3").update_parameters({"Propeller__Direction": -1})

    assert not test_quad_original == test_quad_original2


def test_different_objects():
    assert_different_object_after_parameter_change()
