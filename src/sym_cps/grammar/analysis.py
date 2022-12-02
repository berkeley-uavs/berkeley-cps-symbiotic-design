import json
import math
from collections import Counter
from os import truncate

from sym_cps.grammar import Grammar
from sym_cps.shared.paths import grammar_rules_processed_path, grammar_statistics
from sym_cps.tools.my_io import save_to_file

rule_dict_path_constant = grammar_rules_processed_path

stats = {}
rule_stats = Counter()
rule_stats_dirs = Counter()
keys_stats_dict = Counter()

grammar = Grammar.from_json(rules_json_path=grammar_rules_processed_path)
for rule in grammar.rules:
    visited = []
    rule_keys = set()
    for direction, symbol_types in rule.conditions.__dict__.items():
        if isinstance(symbol_types, set):
            for symbol_type in symbol_types:
                if symbol_type not in visited:
                    for k, values in rule.conditions.__dict__.items():
                        if isinstance(values, set):
                            if symbol_type in values:
                                rule_keys.add(k)
                    visited.append(symbol_type)
            rule_key = "-".join(sorted(list(rule_keys)))
            if rule_key not in rule_stats.keys():
                rule_stats[rule_key] = 0
            rule_stats[rule_key] += 1
            rule_stats_dirs[rule_key] = len(rule_keys)
            for k in rule_keys:
                keys_stats_dict[k] += 1

results = rule_stats.most_common()
results_str = ""

results_str += f"MOST POPULAR\n"
for key, occurances in results:
    results_str += f"{key}\t{occurances}\n"

rule_stats_dirs_order = rule_stats_dirs.most_common()
results_str += f"\n\nMOST DIRECTIONS\n"
for key, occurances in rule_stats_dirs_order:
    results_str += f"{key}\t{occurances}\n"

keys_stats_dict_order = keys_stats_dict.most_common()
results_str += f"\n\nMOST POP KEYS\n"
most_common_keys = []
for key, occurances in keys_stats_dict_order:
    most_common_keys.append(key)
    results_str += f"{key}\t{occurances}\n"

center = int((len(most_common_keys) + 1) / 2)

best_assigment = {}

for i, key in enumerate(most_common_keys):
    even = (i % 2) == 0
    distance = math.floor((i+1) / 2)
    if even:
        best_assigment[key] = center + distance
    else:
        best_assigment[key] = center - distance

results_str += f"\n\nBEST ASSIGNMENT\n"
for key, position in best_assigment.items():
    results_str += f"{key}\t{position}\n"

save_to_file(results_str, absolute_path=grammar_statistics)
