import json
from copy import deepcopy
from itertools import combinations

from sym_cps.shared.designs import designs
from sym_cps.tools.io import save_to_file

designs_to_analyze = [designs["TestQuad"][0], designs["NewAxe"][0]]


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


def learn_swri_parameters(data: dict):
    swri_learned_parameters = {
        "PARAMETERS": {
            "ALL": {"DESCRIPTION": "All parameter values across the seed designs", "VALUES": {}},
            "SHARED": {"DESCRIPTION": "All parameters with same values across the seed designs", "VALUES": {}},
            "DIFFERENT": {"DESCRIPTION": "All parameters with different values across the seed designs", "VALUES": {}},
            "DESIGN_PARAMS_ALL": {
                "DESCRIPTION": "All parameters controlled by DesignParameters in any design",
                "VALUES": [],
            },
            "DESIGN_PARAMS_SHARED": {
                "DESCRIPTION": "All parameters controlled by DesignParameters in every design",
                "VALUES": [],
            },
        }
    }

    p_all = swri_learned_parameters["PARAMETERS"]["ALL"]["VALUES"]
    for d in data.keys():
        all_params = deepcopy(data[d]["PARAMETERS"]["DEFAULT"])
        all_params.update(data[d]["PARAMETERS"]["MODIFIED"])
        for comp_para, instance_params in all_params.items():
            if comp_para not in p_all.keys():
                p_all[comp_para] = []
            for inst_value in instance_params.values():
                if inst_value not in p_all[comp_para]:
                    p_all[comp_para].append(inst_value)

    p_shared = swri_learned_parameters["PARAMETERS"]["SHARED"]["VALUES"]
    p_different = swri_learned_parameters["PARAMETERS"]["DIFFERENT"]["VALUES"]

    for comp_para, values in p_all.items():
        if len(values) == 1:
            p_shared[comp_para] = values[0]
        else:
            if comp_para not in p_different.keys():
                p_different[comp_para] = []
            p_different[comp_para].extend(values)

    all_dp: list[set] = []
    for design_name, infos in data.items():
        all_dp.append(set(infos["PARAMETERS_ASSIGNED"]))

    union = set().union(*all_dp)
    swri_learned_parameters["PARAMETERS"]["DESIGN_PARAMS_ALL"]["VALUES"] = list(union)
    swri_learned_parameters["PARAMETERS"]["DESIGN_PARAMS_SHARED"]["VALUES"] = list(union.intersection(*all_dp))

    return swri_learned_parameters


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
        save_to_file(
            str(json.dumps(info, sort_keys=True, indent=4)), f"parameters.json", folder_name=f"analysis/{design_name}"
        )

    learned_parameters = learn_swri_parameters(data)
    save_to_file(
        str(json.dumps(learned_parameters, sort_keys=True, indent=4)),
        f"learned_parameters.json",
        folder_name=f"analysis",
    )
