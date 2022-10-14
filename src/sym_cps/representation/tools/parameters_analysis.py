import json
from copy import deepcopy
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
        p_assigned = data[design.name]["PARAMETERS_ASSIGNED"] = []
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
                if lib_p not in p_assigned:
                    p_assigned.append(lib_p)
    return data


def extract_shared_parameters(data: dict):
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
    return shared_parameters


if __name__ == "__main__":
    data = parse_designs()
    for design_name, info in data.items():
        save_to_file(str(json.dumps(info, sort_keys=True, indent=4)), f"parameters.json",
                     folder_name=f"analysis/{design_name}")
    shared_parameters = extract_shared_parameters(data)
    save_to_file(str(json.dumps(shared_parameters, sort_keys=True, indent=4)), f"shared_parameters.json",
                 folder_name=f"analysis")

    parameters_assigned_union = set()
    parameters_assigned_shared = set()
    for design_name, infos in data.items():
        parameters_assigned_union |= set(infos["PARAMETERS_ASSIGNED"])

    parameters_assigned_shared = deepcopy(parameters_assigned_union)

    for design_name, infos in data.items():
        d_params = set(infos["PARAMETERS_ASSIGNED"])
        diff = parameters_assigned_shared - d_params
        parameters_assigned_shared = parameters_assigned_shared - diff

    save_to_file("\n".join(parameters_assigned_union), f"parameters_assigned_union",
                 folder_name=f"analysis")

    save_to_file("\n".join(parameters_assigned_shared), f"parameters_assigned_shared",
                 folder_name=f"analysis")

    parameters_assigned_shared_different = deepcopy(parameters_assigned_shared)

    parameters_assigned_shared_different -= set(shared_parameters.keys())

    save_to_file("\n".join(parameters_assigned_shared_different), f"parameters_assigned_shared_different",
                 folder_name=f"analysis")
