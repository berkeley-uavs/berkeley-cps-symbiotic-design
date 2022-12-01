import json

from sym_cps.shared.paths import data_folder, grammar_rules_processed_path
from sym_cps.tools.my_io import save_to_file

symbol_groups = {
    "BODY": ["FUSELAGE", "HUB", "TUBE"],
    "CONNECTOR": ["HUB", "TUBE"],
    "ANYTHING": ["FUSELAGE", "HUB", "TUBE", "WING", "ROTOR", "CONNECTOR"],
    "NON-WING": ["FUSELAGE", "HUB", "TUBE", "WING", "ROTOR", "CONNECTOR", "EMPTY", "UNOCCUPIED", "BOUNDARY"],
    "FREE": ["UNOCCUPIED", "EMPTY", ""],
    "WING-LEFT": ["FUSELAGE", "CONNECTOR", "ROTOR", "WING"],
    "WING-RIGHT": ["EMPTY", "UNOCCUPIED", "CONNECTOR", "ROTOR", "BOUNDARY"],
    "WING-TOP": ["EMPTY", "UNOCCUPIED", "CONNECTOR", "WING", "BOUNDARY"],
    "WING_FRONT": ["EMPTY", "UNOCCUPIED", "CONNECTOR", "ROTOR", "BOUNDARY"],
}

rule_dict_path_constant = data_folder / "reverse_engineering" / "grammar_rules_new.json"

rule_dict = json.load(open(rule_dict_path_constant))
new_rule_dict = {}

for i, (rule_key, items) in enumerate(rule_dict.items()):
    new_conditions = {}
    for dir, conds in items["conditions"].items():
        new_conds = []
        for cond in conds:
            if cond == "BOUNDARY":
                continue
            if cond in symbol_groups.keys():
                new_conds.extend(symbol_groups[cond])
            else:
                new_conds.append(cond)
        new_conditions[dir] = new_conds
    new_rule_dict[f"r{i}"] = {
        "name": rule_key,
        "conditions": new_conditions,
        "production": items["production"]
    }


save_to_file(new_rule_dict, absolute_path=grammar_rules_processed_path)