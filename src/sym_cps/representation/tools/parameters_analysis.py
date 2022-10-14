import json
from itertools import combinations

from sym_cps.shared.library import designs
from sym_cps.tools.io import save_to_file

designs_to_analyze = [
    designs["TestQuad"][0],
    designs["NewAxe"][0]
]


def _all_same_value(dictionary: dict) -> bool:
    value = list(dictionary.values())[0]
    for p, p_value in dictionary.items():
        print(f"Checking for {p_value}: {value}")
        if p_value != value:
            return False
    return True


def parse_designs():
    data = {}
    for design in designs_to_analyze:
        data[design.name] = {}
        data[design.name]["PARAMETERS"] = {}
        data[design.name]["PARAMETERS"]["DEFAULT"] = {}
        data[design.name]["PARAMETERS"]["MODIFIED"] = {}
        data[design.name]["PARAMETERS"]["COMPONENT"] = {}
        data[design.name]["DESIGN_PARAMETERS"] = {}
        p_default = data[design.name]["PARAMETERS"]["DEFAULT"]
        p_modified = data[design.name]["PARAMETERS"]["MODIFIED"]
        p_component = data[design.name]["PARAMETERS"]["COMPONENT"]
        p_design = data[design.name]["DESIGN_PARAMETERS"]
        for parameter in design.parameters:
            if parameter.value != parameter.default:
                if parameter.c_parameter.id not in p_default.keys():
                    p_default[parameter.c_parameter.id] = {}
                p_default[parameter.c_parameter.id][parameter.id] = parameter.value
            else:
                if parameter.c_parameter.id not in p_modified.keys():
                    p_modified[parameter.c_parameter.id] = {}
                p_modified[parameter.c_parameter.id][parameter.id] = parameter.value
        for parameter in design.parameters:
            if parameter.c_parameter.id in p_default:
                param_dict = p_default[parameter.c_parameter.id]
            else:
                param_dict = p_modified[parameter.c_parameter.id]
            all_same = True
            first_value = list(param_dict.values())[0]
            for param, value in param_dict.items():
                if value != first_value:
                    all_same = False
            if all_same:
                p_component[parameter.c_parameter.id] = first_value
        for dp in design.design_parameters.values():
            p_design[dp.id] = {"VALUE": dp.value, "PARAMETERS": {}}
            for parameter in dp.parameters:
                lib_p = parameter.c_parameter.id
                if lib_p not in p_design[dp.id]["PARAMETERS"].keys():
                    p_design[dp.id]["PARAMETERS"][lib_p] = []
                p_design[dp.id]["PARAMETERS"][lib_p].append(parameter.id)
    return data


if __name__ == "__main__":
    data = parse_designs()
    for design_name, info in data.items():
        save_to_file(str(json.dumps(info)), f"parameters.json", folder_name=f"analysis/{design_name}")
    shared_parameters = {}
    for (d_a, d_b) in combinations(data.keys(), 2):
        comp_a = data[d_a]["PARAMETERS"]["COMPONENT"]
        comp_b = data[d_b]["PARAMETERS"]["COMPONENT"]
        shared_keys = set(comp_a.keys()) & set(comp_b.keys())
        shared_keys_values = filter(lambda x: comp_b[x] == comp_a[x], shared_keys)
        for k in shared_keys_values:
            shared_parameters[k] = comp_a[k]
    save_to_file(str(json.dumps(shared_parameters)), f"shared_parameters.json", folder_name=f"analysis")
