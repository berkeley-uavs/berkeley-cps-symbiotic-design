from pathlib import Path
import json
import platform

from sym_cps.optimizers import Optimizer
from sym_cps.optimizers.control_opt.control_opt_bayes import ControlBayesOptimizer
from sym_cps.shared.paths import fdm_extract_folder, fdm_bin_folder, fdm_root_folder, fdm_tmp_folder

class ControlOptimizer(Optimizer):

    def optimize(self,
        d_concrete: DConcrete,
        file_path: str = None
    ) -> DConcrete:
        if platform.system() == "Windows": #windows
            fdm_path = fdm_root_folder / "bin" / "bin" / "bin" / "new_fdm.exe"
        elif platform.system() == "Darwin":
            fdm_path = fdm_root_folder / "source" / "flight-dynamics-model" / "bin" / "new_fdm"
        elif platform.system() == "Linuex":
            print("Error, need someone to provide an fdm binary!")

        # table_path = fdm_root_folder / "Tables" / "PropData"
        table_path = "./fdm/Tables/PropData"
        ret_path   = fdm_extract_folder / f"control_opt_result.json" 

        if file_path is None:
            file_path = fdm_extract_folder / "flightDynFast.inp"
        # fdm_files_folder_path = os.path.join(current_working_dir, "TestBench_FlightDynTB_V1")
        # fdm_input_file = os.path.join(fdm_files_folder_path, "FlightDyn.inp")
        # print(fdm_input_file)


        # file_path = os.path.join(os.path.dirname(__file__), "..", "..", "fdm", "Trowel", "flightDyn.inp")
        opt = ControlBayesOptimizer(file_path, method="all_bayes", num_grids=None, fdm_exec=fdm_path, table_path=table_path)
        # opt.set_speed_bounds("requested_vertical_speed", max_val = 2, min_val = 1)
        best_trim = opt.get_suggested_speed()
        # print(best_trim)
        # opt.set_speed_bounds("requested_lateral_speed", max_val = best_trim, min_val = best_trim-1)
        # opt.set_control_bounds("Q_position", max_val = 0.41, min_val = 0.4)
        opt.set_control_bounds("R", max_val = 1.000, min_val = 0.001)
        # opt.set_num_grids(num_grids)
        ret = opt.optimize(**{"best_trim": best_trim, "n_iter": 10, "init_points": 1})

        #print(ret)
        with open(ret_path, "w") as file:
            json.dump(ret, file)

        return ret