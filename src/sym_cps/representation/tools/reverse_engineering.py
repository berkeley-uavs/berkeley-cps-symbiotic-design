import json
from copy import deepcopy

from sym_cps.shared.library import designs
from sym_cps.tools.io import save_to_file

quad = designs["TestQuad"][0]
axe = designs["NewAxe"][0]


def design_parameters():
    print("TestQuad DP")
    for dp in quad.design_parameters.values():
        print(dp)

    print("NewAxe DP")
    for dp in axe.design_parameters.values():
        print(dp)


def _all_same_value(dictionary: dict) -> bool:
    value = list(dictionary.values())[0]
    for p, p_value in dictionary.items():
        print(f"Checking for {p_value}: {value}")
        if p_value != value:
            return False
    return True

def parameters():
    designs_chosen = {"quad": quad, "axe": axe}

    data = {
        "axe_all": {},
        "axe_default": {},
        "axe_modified": {},
        "quad_all": {},
        "quad_default": {},
        "quad_modified": {},
        "all_defaults": {},
        "shared_default": {},
        "shared_modified": {},
        "shared_modified_different": {},
        "axe_minimal": {},
        "quad_minimal": {},
        "axe_minimal_parameters": {},
        "quad_minimal_parameters": {}
    }

    for name_a, design_a in designs_chosen.items():
        data[f"{name_a}_all"] = {}
        data[f"{name_a}_modified"] = {}
        data[f"{name_a}_default"] = {}
        for parameter in design_a.parameters:
            data[f"all_defaults"][parameter.c_parameter.id] = parameter.default
            if parameter.c_parameter.id not in data[f"{name_a}_all"].keys():
                data[f"{name_a}_all"][parameter.c_parameter.id] = {}
            data[f"{name_a}_all"][parameter.c_parameter.id][parameter.id] = parameter.value
            if parameter.value != parameter.default:
                if parameter.c_parameter.id not in data[f"{name_a}_modified"].keys():
                    data[f"{name_a}_modified"][parameter.c_parameter.id] = {}
                data[f"{name_a}_modified"][parameter.c_parameter.id][parameter.id] = parameter.value
            else:
                if parameter.c_parameter.id not in data[f"{name_a}_default"].keys():
                    data[f"{name_a}_default"][parameter.c_parameter.id] = {}
                data[f"{name_a}_default"][parameter.c_parameter.id][parameter.id] = parameter.value

    for param_lib_id, param in data["axe_default"].items():
        value = list(param.values())[0]
        if param_lib_id in data["quad_default"].keys():
            data["shared_default"][param_lib_id] = value

    for param_lib_id, param in data["axe_modified"].items():
        if not _all_same_value(param):
            continue
        value_a = list(param.values())[0]
        print(f"Checking for {param_lib_id}: {value}")
        if param_lib_id in data["quad_modified"].keys():
            if not _all_same_value(data["quad_modified"][param_lib_id]):
                continue
            value_b = list(data["quad_modified"][param_lib_id].values())[0]
            if value_a != value_b:
                data["shared_modified_different"][param_lib_id] = {"axe": value_a, "quad": value_b}
            else:
                data["shared_modified"][param_lib_id] = value

    data["axe_minimal"] = deepcopy(data["axe_all"])
    data["quad_minimal"] = deepcopy(data["quad_all"])

    default_keys = set(data["shared_modified"].keys()) | set(data["shared_default"].keys())
    
    for name in {"axe", "quad"}:
        for k in default_keys:
            if k in data[f"{name}_minimal"].keys():
                del data[f"{name}_minimal"][k]

        pid_in_design_parameters = set()
        for dp in axe.design_parameters.values():
            data[f"{name}_minimal_parameters"][dp.id] = {"VALUE": dp.value, "PARAMETERS": []}
            for parameter in dp.parameters:
                lib_p = parameter.c_parameter.id
                if lib_p in data[f"{name}_minimal"].keys():
                    data[f"{name}_minimal_parameters"][dp.id]["PARAMETERS"].append(parameter.id)
                    pid_in_design_parameters |= {parameter.id}
                else:
                    print(f"{dp.id} skipped")
            data[f"{name}_minimal_minus_params"] = deepcopy(data[f"{name}_minimal"])
            for k, v in data[f"{name}_minimal"].items():
                for vk, v in v.items():
                    if vk in pid_in_design_parameters:
                        print(f"{vk} in {pid_in_design_parameters}")
                        del data[f"{name}_minimal_minus_params"][k][vk]
                    
        for name, info in data.items():
            # info = sorted(info.items(), key=lambda x: x[0])
            save_to_file(str(json.dumps(info)), f"{name}.json", folder_name="analysis")


if __name__ == "__main__":
    parameters()
