import base64
import hashlib


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


def get_instance_name(component_type_name: str, instance_id: int) -> str:
    if component_type_name == "Orient":
        return "Orient"
    return f"{component_type_name}_instance_{instance_id}"


def rename_instance(instance: str, c_type_id: str, instances_renaming: dict, instances_created: dict):
    instances_renaming[instance] = instance
    return
    # if "Orient" in c_type_id:
    #     return
    # if c_type_id not in instances_created.keys():
    #     instances_created[c_type_id] = 1
    # else:
    #     instances_created[c_type_id] = instances_created[c_type_id] + 1
    # new_name = get_instance_name(c_type_id, c_type_id)
    # instances_renaming[instance] = new_name


# def sort_dictionary(element: dict):
#     ordered_dict = {}
#     for k, v in sorted(element.items()):
#         if isinstance(v, dict):
#             ordered_dict = sort_dictionary(v)
#         else:
#             ordered_dict[k] = v
#
#     return ordered_dict


def sort_dictionary(d):
    try:
        if isinstance(d, list):
            for v in d:
                sort_dictionary(v)
            # return sorted(sort_dictionary(v) for v in d)
        if isinstance(d, dict):
            new_dict = {}
            for k in sorted(list(d.keys())):
                new_dict[k] = sort_dictionary(d[k])
            return new_dict
            # return {k: sort_dictionary(d[k]) for k in sorted(list(d.keys()))}
        return d
    except Exception as e:
        print(e)
    return d


#
# def sort_dictionary(obj: dict):
#     if isinstance(obj, dict):
#         obj = sorted(obj.items())
#         for k, v in obj.items():
#             if isinstance(v, dict) or isinstance(v, list):
#                 obj[k] = sort_dictionary(v)
#
#     if isinstance(obj, list):
#         for i, v in enumerate(obj):
#             if isinstance(v, dict) or isinstance(v, list):
#                 obj[i] = sort_dictionary(v)
#         obj = sorted(obj, key=lambda x: json.dumps(x))
#
#     return obj


def get_component_type_from_instance_name(instance: str):
    if "_instance_" in instance:
        return instance.split("_instance_")[0]
    return instance


def get_component_and_instance_type_from_instance_name(instance: str) -> (str, int):
    if "_instance_" in instance:
        return instance.split("_instance_")[0], instance.split("_instance_")[1]
    return instance, 0


def make_hash_sha256(o):
    hasher = hashlib.sha256()
    hasher.update(repr(make_hashable(o)).encode())
    return base64.b64encode(hasher.digest()).decode()


def make_hashable(o):
    if isinstance(o, (tuple, list)):
        return tuple((make_hashable(e) for e in o))

    if isinstance(o, dict):
        return tuple(sorted((k, make_hashable(v)) for k, v in o.items()))

    if isinstance(o, (set, frozenset)):
        return tuple(sorted(make_hashable(e) for e in o))

    return o
