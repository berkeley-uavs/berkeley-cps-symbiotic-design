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
