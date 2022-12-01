from __future__ import annotations

from dataclasses import dataclass

from sym_cps.grammar import Rule, Grammar
from sym_cps.shared.paths import data_folder, grammar_rules_processed_path

rule_dict_path_constant = data_folder / "reverse_engineering" / "grammar_rules_new.json"


@dataclass
class Contract:
    assumptions: list[str]
    guarantees: dict[tuple, list[tuple]]
    name: str = ""

    @classmethod
    def from_rule(cls, rule: Rule) -> Contract:
        pass


if __name__ == '__main__':
    contracts = []
    grammar = Grammar.from_json(rules_json_path=grammar_rules_processed_path)
    for rule in grammar.rules:
        c = Contract.from_rule(rule)
        contracts.append(c)
