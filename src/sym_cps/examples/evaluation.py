# type: ignore

from sym_cps.evaluation import evaluate_design
from sym_cps.shared.paths import designs_folder

design_json_path = designs_folder / "Trowel/design_swri.json"

if __name__ == '__main__':

    """Generate info"""
    evaluate_design(design_json_path=design_json_path,
                    metadata={"extra_info": "design_example_default_info_only"},
                    timeout=800,
                    info_only=True)

    # """Full evaluation of design"""
    evaluate_design(design_json_path=design_json_path,
                    metadata={"extra_info": "full evaluation example"},
                    timeout=800)

