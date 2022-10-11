from sym_cps.optimizers.control_opt.control_opt_bayes import ControlBayesOptimizer
import json
import os
import sys

if __name__ == "__main__":
    """python -m control_opt_interface <FDM_INPUT_FILE>"""

    #fdm_path = r"C:\jwork\Agents\workspace\UAM_Workflows\FlightDynamics"
    #table_path = r"C:\jwork\Agents\workspace\UAM_Workflows\Tables\PropData"
    fdm_path = None
    table_path = None
    file_path = sys.argv[1]

    #file_path = os.path.join(os.path.dirname(__file__), "..", "..", "fdm", "Trowel", "flightDyn.inp")
    opt = ControlBayesOptimizer(file_path, method="all_bayes", num_grids=None, fdm_exec=fdm_path, table_path=table_path)
    #opt.set_speed_bounds("requested_vertical_speed", max_val = 2, min_val = 1)
    best_trim = opt.get_suggested_speed()
    #print(best_trim)
    #opt.set_speed_bounds("requested_lateral_speed", max_val = best_trim, min_val = best_trim-1)
    #opt.set_control_bounds("Q_position", max_val = 0.41, min_val = 0.4)
    #opt.set_control_bounds("Q_velocity", max_val = 0.31, min_val = 0.3)
    #opt.set_num_grids(num_grids)
    ret = opt.optimize(**{"best_trim": best_trim, "n_iter": 2, "init_points": 1})

    print(ret)
    with open("control_opt_result.json", "w") as file:
        json.dump(ret, file)


