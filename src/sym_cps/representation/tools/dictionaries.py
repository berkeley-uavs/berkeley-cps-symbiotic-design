def number_of_instances_in_dict(dictionary: dict, instance: str, n=0):
    for k, v in dictionary.items():
        if instance == k:
            n += 1
        if isinstance(v, dict):
            return number_of_instances_in_dict(v, instance, n)
        else:
            if instance == v:
                n += 1
    return n


def connector_id(name: str, component_type: str):
    return f"{component_type}__{name}"
