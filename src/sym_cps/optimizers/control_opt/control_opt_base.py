import math

from sym_cps.evaluation.fdm_interface import FDMArgs, FDMInterface


class ControlOptimizer(object):
    def __init__(self, fdm_input_path, fdm_exec=None, table_path=None):
        self._fdm_interface = FDMInterface(fdm_path=fdm_exec, table_path=table_path)
        self._fdm_data = self._fdm_interface.read_fdm_input(fdm_input_path)
        self._fdm_args = FDMArgs(self._fdm_data)
        # constraints in the domain
        # self._paths = [4, 1, 3, 5]
        self._paths = [9]
        self._control_bound = {
            "Q_position": {"max": 1.0, "min": 0.0},
            "Q_velocity": {"max": 1.0, "min": 0.0},
            "Q_angular_velocity": {"max": 1.0, "min": 0.0},
            "Q_angles": {"max": 1.0, "min": 0.0},
            "R": {"max": 1.0, "min": 0.0},
        }
        self._speed_bound = {
            "requested_lateral_speed": {"max": 50.0, "min": 0.0},
            "requested_vertical_speed": {"max": 0.0, "min": -2.0},
        }
        # variable names
        self._path_var_names = ["i_flight_path"]
        self._speed_var_names = self._speed_bound.keys()
        self._control_var_names = self._control_bound.keys()
        self._lspeed_hovering = 0

    def set_paths(self, paths):
        self._paths = paths

    def set_lspeed_hovering(self, speed):
        self._lspeed_hovering = speed

    def set_speed_bounds(self, name, max_val=None, min_val=None):
        if max_val is not None:
            self._speed_bound[name]["max"] = max_val
        if min_val is not None:
            self._speed_bound[name]["min"] = min_val

    def set_control_bounds(self, name, max_val=None, min_val=None):
        if max_val is not None:
            self._control_bound[name]["max"] = max_val
        if min_val is not None:
            self._control_bound[name]["min"] = min_val

    def raw_score(self, path, fdm_output):
        score = None
        flight_time = fdm_output.get_metrics("Time_to_traverse_path")[0]
        flight_error = fdm_output.get_metrics("Maximimum_error_distance_during_flight")[0]
        flight_distance = fdm_output.get_metrics("Flight_distance")[0]
        if path == 4:  # rise and hovering
            score = flight_time - 20 * math.fabs(150 - flight_distance)
        elif path == 1:  # straight flight
            score = flight_distance - 10 * flight_error
        elif path == 3:  # circle
            score = fdm_output.get_metrics("Score")
        elif path == 5:  # oval
            score = fdm_output.get_metrics("Score")
        elif path == 6:  # straight line acceleration
            score = fdm_output.get_metrics("Score")
        elif path == 7:  # Path 7 – vertical to horizontal transition
            score = fdm_output.get_metrics("Score")
        elif path == 8:  # Path 8 – horizontal to vertical transition
            score = fdm_output.get_metrics("Score")
        elif path == 9:  # hackathon, and is the superset of paths 6-8
            score = fdm_output.get_metrics("Score")
        else:
            raise Exception("Not supported path!")
        return score

    def get_suggested_speed(self):
        fdm_output = self._fdm_interface.execute_from_data(self._fdm_data, self._fdm_args)
        trim_state_dict = fdm_output.fastest_trim_state
        return trim_state_dict

    def optimize_path(self, path=1, **kwargs):
        pass

    def _method(self, path=1, **kwargs):
        pass

    def optimize(self, **kwargs):
        ret = []
        print("Search Space: ")
        print(self._speed_spaces)
        for path in self._paths:
            path_ret = self._method(path, **kwargs)
            if path_ret["best_score"] <= 0 and path == 4:
                break
            ret.append(path_ret)
        ret, total_score = self.output_collection(ret)
        return {"result": ret, "total_score": total_score}

    def output_collection(self, ret):
        total_score = 0
        for path_ret in ret:
            fdm_args = path_ret["best_args"]
            print(fdm_args)
            fdm_output = self._fdm_interface.execute_from_data(self._fdm_data, fdm_args)
            score = fdm_output.get_metrics("Score")
            #score = 100
            #print("warning! FDM result file is not actually using yet")
            path_ret["raw_score"] = path_ret["best_score"]
            path_ret["best_score"] = score
            path_ret["best_args"] = fdm_args.args
            total_score += score
        return ret, total_score

    # def _pack_args(self, **kwargs):
    #     fdm_args = FDMArgs(None,
    #                 **{"i_flight_path": path,
    #                   "requested_lateral_speed": lspeed,
    #                   "requested_vertical_speed" : vspeed,
    #                   "Q_position" : Q_position ,
    #                   "Q_velocity" : Q_velocity ,
    #                   "Q_angular_velocity" : Q_angular_velocity ,
    #                   "Q_angles" : Q_angles ,
    #                   "R": R
    #                   })
    #     return fdm_args
