from __future__ import annotations

from dataclasses import dataclass

from gear.terms.polyhedra import PolyhedralTerm
from sym_cps.grammar import Rule, Grammar, Direction
from sym_cps.shared.paths import data_folder, grammar_rules_processed_path

rule_dict_path_constant = data_folder / "reverse_engineering" / "grammar_rules_new.json"



@dataclass
class Contract:
    assumptions: list[str]
    guarantees: dict[tuple, list[tuple]]
    name: str = ""

    @classmethod
    def from_rule(cls, rule: Rule) -> Contract:

        all_dirs = {}
        for direction, symbol_types in rule.conditions.__dict__.items():
            all_dirs[direction]: list[str] = []
            if isinstance(symbol_types, set):
                for symbol_type in symbol_types:
                    term_str = f"{Direction[direction].value}<= {symbol_type.name} <{Direction[direction].value}"
                    print(term_str)
                    polyhedra_term = PolyhedralTerm.from_string(term_str)
                    all_dirs[direction].append(polyhedra_term)

        for symbol_type in rule.conditions.front:
            str_rep = f"<= {symbol_type.name} <"
            PolyhedralTerm.from_string()
        new_term = PolyhedralTerm.from_string()


if __name__ == '__main__':
    contracts = []
    grammar = Grammar.from_json(rules_json_path=grammar_rules_processed_path)
    for rule in grammar.rules:
        c = Contract.from_rule(rule)
        contracts.append(c)
