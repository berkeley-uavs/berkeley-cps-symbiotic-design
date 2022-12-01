from __future__ import annotations

from dataclasses import dataclass

from sym_cps.shared.paths import data_folder

rule_dict_path_constant = data_folder / "reverse_engineering" / "grammar_rules_new.json"


@dataclass
class Contract:
    assumptions: list[str]
    guarantees: dict[tuple, list[tuple]]
    name: str = ""

    def fr



