# type: ignore

from sym_cps.evaluation import evaluate_design, generate_info_files
from sym_cps.shared.paths import output_folder


def example_evaluate_design_json():
    design_json_path = output_folder / "Trowel/design_swri.json"
    evaluate_design(design_json_path)


def example_generate_info_design():
    design_json_path = output_folder / "Trowel/design_swri.json"
    generate_info_files(design_json_path)


if __name__ == '__main__':
    example_evaluate_design_json()
    # example_generate_info_design()
