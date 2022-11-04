import math
import os

import numpy as np

from sym_cps.optimizers.control_opt.control_opt_base import ControlOptimizer
from sym_cps.evaluation.fdm_interface import FDMArgs


class ControlGridOptimizer(ControlOptimizer):
    def __init__(self, fdm_input_path, fdm_exec=None, num_grids=None):
        super().__init__(fdm_input_path, fdm_exec)
        self._method = self.optimize_path
        # default_grids
        _num_grids = {
            "requested_lateral_speed": 5,
            "requested_vertical_speed": 5,
            "Q_position": 3,
            "Q_velocity": 3,
            "Q_angular_velocity": 3,
            "Q_angles": 3,
            "R": 3,
        }
        # set the provided value to _num_grids if the key exists
        # print(num_grids)
        if num_grids is not None:
            for name, num in num_grids.items():
                _num_grids[name] = num
        # print(_num_grids)
        self.set_num_grids(_num_grids)

    def set_num_grids(self, num_grids):
        self._set_num_grids_speed(num_grids)
        self._set_num_grids_control(num_grids)

    def _set_num_grids_speed(self, num_grids):
        # set speed
        self._speed_spaces = {}
        for name in self._speed_var_names:
            min_bound = self._speed_bound[name]["min"]
            max_bound = self._speed_bound[name]["max"]
            ngrids = num_grids[name]
            self._speed_spaces[name] = np.linspace(min_bound, max_bound, ngrids + 1)[1:]

    def _set_num_grids_control(self, num_grids):
        self._control_spaces = {}
        for name in self._control_var_names:
            min_bound = self._control_bound[name]["min"]
            max_bound = self._control_bound[name]["max"]
            ngrids = num_grids[name]
            self._control_spaces[name] = np.linspace(min_bound, max_bound, ngrids)

    def optimize_path(self, path=1, **kwargs):

        best_score = -math.inf
        best_args = None
        # reset values to handle vertical speed and lateral speed for path 4
        if path == 4:
            speeds = self._speed_spaces["requested_vertical_speed"]
        else:
            speeds = self._speed_spaces["requested_lateral_speed"]

        for speed in speeds:
            vspeed = speed if path == 4 else 0
            lspeed = 0 if path == 4 else speed
            for Q_position in self._control_spaces["Q_position"]:
                for Q_velocity in self._control_spaces["Q_velocity"]:
                    for Q_angular_velocity in self._control_spaces["Q_angular_velocity"]:
                        for Q_angles in self._control_spaces["Q_angles"]:
                            for R in self._control_spaces["R"]:
                                fdm_args = FDMArgs(
                                    None,
                                    **{
                                        "i_flight_path": path,
                                        "requested_lateral_speed": lspeed,
                                        "requested_vertical_speed": vspeed,
                                        "Q_position": Q_position,
                                        "Q_velocity": Q_velocity,
                                        "Q_angular_velocity": Q_angular_velocity,
                                        "Q_angles": Q_angles,
                                        "R": R,
                                    },
                                )
                                print(
                                    f"path = {path}, vs = {vspeed}, ls = {lspeed}, Q_postion = {Q_position}, Q_velocity = {Q_velocity}, Q_angular_velocity = {Q_angular_velocity}, Q_angles = {Q_angles}, R = {R}"
                                )
                                fdm_output = self._fdm_interface.execute_from_data(self._fdm_data, fdm_args)
                                score = fdm_output.get_metrics("Score")
                                raw_score = self.raw_score(path, fdm_output)
                                print(f"score = {score}, raw_score = {raw_score}")
                                if score > best_score:
                                    best_score = score
                                    best_args = fdm_args
        return {"Path": path, "best_score": best_score, "best_args": best_args}


if __name__ == "__main__":
    num_grids = {
        "requested_lateral_speed": 1,
        "requested_vertical_speed": 1,
        "Q_position": 1,
        "Q_velocity": 1,
        "Q_angular_velocity": 2,
        "Q_angles": 2,
        "R": 2,
    }
    file_path = os.path.join(os.path.dirname(__file__), "..", "..", "fdm", "Trowel", "flightDyn.inp")
    opt = ControlGridOptimizer(file_path, num_grids=num_grids)
    opt.set_speed_bounds("requested_vertical_speed", max_val=2, min_val=1)
    opt.set_speed_bounds("requested_lateral_speed", max_val=16, min_val=15)
    opt.set_control_bounds("Q_position", max_val=0.41, min_val=0.4)
    opt.set_control_bounds("Q_velocity", max_val=0.31, min_val=0.3)
    opt.set_num_grids(num_grids)
    print(opt.optimize())
