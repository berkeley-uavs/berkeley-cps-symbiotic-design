def tab(stringable_object) -> str:
    return "\n".join(list(map(lambda x: f"\t{x}", str(stringable_object).splitlines())))


def repr_dictionary(dictionary: dict) -> str:
    ret = ""
    for key, value in dictionary.items():
        if hasattr(value, "__iter__"):
            val = "\n\t".join([_str_value(v) for v in value])
            ret += f"{_str_value(key)} ({len(value)} items):\n\t{val}\n"
        else:
            ret += f"{_str_value(key)}: \t{_str_value(value)}\n"
    return ret


def _str_value(value) -> str:
    if isinstance(value, float) or isinstance(value, int):
        return str(value)
    if not isinstance(value, str):
        if hasattr(value, "id"):
            return value.id
        if hasattr(value, "name"):
            return value.name
        else:
            raise AttributeError
    return value


def rename_component_types(component_type: str) -> str:
    return component_type


def rename_instance(instance: str, c_type_id: str, instances_renaming: dict, instances_created: dict):
    instances_renaming[instance] = instance
    if "Orient" in c_type_id:
        return
    if c_type_id not in instances_created.keys():
        instances_created[c_type_id] = 1
    else:
        instances_created[c_type_id] = instances_created[c_type_id] + 1
    new_name = f"{c_type_id}_instance_{instances_created[c_type_id]}"
    instances_renaming[instance] = new_name


def get_component_type_from_instance_name(instance: str):
    if "_instance_" in instance:
        return instance.split("_instance_")[0]
    return instance


def get_component_and_instance_type_from_instance_name(instance: str) -> (str, int):
    if "_instance_" in instance:
        return instance.split("_instance_")[0], instance.split("_instance_")[1]
    return instance, 0
