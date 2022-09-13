def parameter_id(parameter_name: str, component_type: str):
    return f"{component_type}__{parameter_name}"


def connector_id(name: str, component_type: str):
    return f"{component_type}__{name}"
