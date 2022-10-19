import math
import os

import numpy as np
from bayes_opt import BayesianOptimization

from sym_cps.optimizers.control_opt.control_opt_base import ControlOptimizer
from sym_cps.optimizers.control_opt.fdm_interface import FDMArgs


class ControlBayesOptimizer(ControlOptimizer):
    def __init__(self, fdm_input_path, method="all_bayes", fdm_exec=None, num_grids=None, table_path=None):
        super().__init__(fdm_input_path, fdm_exec=fdm_exec, table_path=table_path)

        if method == "grid_speed":
            self._method = self.optimize_path_grid_speed
            self._num_grids = {
                "requested_lateral_speed": 5,
                "requested_vertical_speed": 5,
            }
            # set the provided value to _num_grids if the key exists
            if num_grids is not None:
                for name, num in num_grids.items():
                    self._num_grids[name] = num

                self.set_num_grids(self._num_grids)
        elif method == "all_bayes":
            self._method = self.optimize_path_all_bayes
        else:
            raise Exception(f"No such method {method}")

    def set_num_grids(self, num_grids):
        self._set_num_grids_speed(num_grids)
        # self._set_num_grids_control(num_grids)

    def _set_num_grids_speed(self, num_grids):
        # set speed
        self._speed_spaces = {}
        for name in self._speed_var_names:
            min_bound = self._speed_bound[name]["min"]
            max_bound = self._speed_bound[name]["max"]
            ngrids = num_grids[name]
            self._speed_spaces[name] = np.linspace(min_bound, max_bound, ngrids + 1)[1:]

    def optimize(self, **kwargs):
        ret = []
        for path in self._paths:
            if "best_trim" in kwargs:
                best_trim = kwargs["best_trim"]
                if path == 1:
                    lspeed = best_trim["Level"]
                    self.set_speed_bounds("requested_lateral_speed", max_val=lspeed, min_val=lspeed - 1)
                elif path == 3:
                    lspeed = best_trim["Turning500"]
                    self.set_speed_bounds("requested_lateral_speed", max_val=lspeed, min_val=lspeed - 1)
                elif path == 5:
                    lspeed = best_trim["Level"]  # best_trim["Turning300"]
                    self.set_speed_bounds("requested_lateral_speed", max_val=lspeed, min_val=lspeed - 1)
            path_ret = self._method(path, **kwargs)
            if path_ret["best_score"] <= 0 and path == 4:
                break
            ret.append(path_ret)
        ret, total_score = self.output_collection(ret)
        return {"result": ret, "total_score": total_score}

    def optimize_path_grid_speed(self, path=1, **kwargs):
        if path == 3:
            if "best_turning_trim" in kwargs.keys():
                # todo implement different strategy for turning trim state and level trim state
                pass
        best_score = -math.inf
        best_args = None
        # reset values to handle vertical speed and lateral speed for path 1

        if path == 4:
            speeds = self._speed_spaces["requested_vertical_speed"]
        else:
            speeds = self._speed_spaces["requested_lateral_speed"]

        for speed in speeds:
            vspeed = speed if path == 4 else 0
            lspeed = 0 if path == 4 else speed

            def dummy_f(Q_position, Q_velocity, Q_angular_velocity, Q_angles, R):
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
                return score

            pbounds = {
                name: (self._control_bound[name]["min"], self._control_bound[name]["max"])
                for name in self._control_var_names
            }
            optimizer = BayesianOptimization(f=dummy_f, pbounds=pbounds, verbose=2, random_state=1)
            optimizer.maximize(
                init_points=3,
                n_iter=20,
            )
            fdm_args = FDMArgs(
                None,
                **{
                    "i_flight_path": path,
                    "requested_lateral_speed": lspeed,
                    "requested_vertical_speed": vspeed,
                    "Q_position": optimizer.max["params"]["Q_position"],
                    "Q_velocity": optimizer.max["params"]["Q_velocity"],
                    "Q_angular_velocity": optimizer.max["params"]["Q_angular_velocity"],
                    "Q_angles": optimizer.max["params"]["Q_angles"],
                    "R": optimizer.max["params"]["R"],
                },
            )

            score = optimizer.max["target"]
            # record
            if score > best_score:
                best_score = score
                best_args = fdm_args

        return {"Path": path, "best_score": best_score, "best_args": best_args}

    def optimize_path_all_bayes(self, path=1, **kwargs):
        init_points = 1
        n_iter = 3
        verbose = (2,)
        random_state = 1
        if "lspeed_hovering" in kwargs:
            self._lspeed_hovering = kwargs["lspeed_hovering"]
        if "init_points" in kwargs:
            init_points = kwargs["init_points"]
        if "n_iter" in kwargs:
            n_iter = kwargs["n_iter"]
        if "verbose" in kwargs:
            verbose = kwargs["verbose"]
        if "random_state" in kwargs:
            random_state = kwargs["random_state"]
        # reset values to handle vertical speed and lateral speed for path 1
        def dummy_f(speed, Q_position, Q_velocity, Q_angular_velocity, Q_angles, R):
            vspeed = speed if path == 4 else 0
            lspeed = self._lspeed_hovering if path == 4 else speed
            # vspeed = math.ceil(vspeed)
            lspeed = math.ceil(lspeed)
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
            #score = 100
            raw_score = self.raw_score(path, fdm_output)
            #raw_score = 100
            #print("warning! FDM result file is not actually using yet")
            print(f"score = {score}, raw_score = {raw_score}")
            # if score == 0 and raw_score > 0:
            #    raise Exception("Zero!!")
            return raw_score

        pbounds = {
            name: (self._control_bound[name]["min"], self._control_bound[name]["max"])
            for name in self._control_var_names
        }
        if path == 4:
            pbounds["speed"] = (
                self._speed_bound["requested_vertical_speed"]["min"],
                self._speed_bound["requested_vertical_speed"]["max"],
            )
        else:
            pbounds["speed"] = (
                self._speed_bound["requested_lateral_speed"]["min"],
                self._speed_bound["requested_lateral_speed"]["max"],
            )

        optimizer = BayesianOptimization(f=dummy_f, pbounds=pbounds, verbose=verbose, random_state=random_state)
        optimizer.maximize(
            init_points=init_points,
            n_iter=n_iter,
        )
        vspeed = optimizer.max["params"]["speed"] if path == 4 else 0
        lspeed = self._lspeed_hovering if path == 4 else optimizer.max["params"]["speed"]
        best_args = FDMArgs(
            None,
            **{
                "i_flight_path": path,
                "requested_lateral_speed": math.ceil(lspeed),
                "requested_vertical_speed": vspeed,
                "Q_position": optimizer.max["params"]["Q_position"],
                "Q_velocity": optimizer.max["params"]["Q_velocity"],
                "Q_angular_velocity": optimizer.max["params"]["Q_angular_velocity"],
                "Q_angles": optimizer.max["params"]["Q_angles"],
                "R": optimizer.max["params"]["R"],
            },
        )

        best_score = optimizer.max["target"]

        return {"Path": path, "best_score": best_score, "best_args": best_args}


if __name__ == "__main__":
    num_grids = {
        "requested_lateral_speed": 1,
        "requested_vertical_speed": 1,
    }
    file_path = os.path.join(os.path.dirname(__file__), "..", "fdm", "Trowel", "flightDyn.inp")
    opt = ControlBayesOptimizer(file_path, method="all_bayes", num_grids=num_grids)
    # opt.set_speed_bounds("requested_vertical_speed", max_val = 2, min_val = 1)
    best_trim = opt.get_suggested_speed()
    print(best_trim)
    # opt.set_speed_bounds("requested_lateral_speed", max_val = best_trim, min_val = best_trim-1)
    # opt.set_control_bounds("Q_position", max_val = 0.41, min_val = 0.4)
    # opt.set_control_bounds("Q_velocity", max_val = 0.31, min_val = 0.3)
    opt.set_num_grids(num_grids)
    ret = opt.optimize(**{"best_trim": best_trim, "n_iter": 10, "init_points": 3})
    print(ret)
