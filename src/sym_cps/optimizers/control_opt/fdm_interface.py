import os

from sym_cps.optimizers.control_opt.fdm_data import FDMData
from sym_cps.optimizers.control_opt.fdm_ret import FDMResult
from sym_cps.shared.paths import fdm_bin_folder, fdm_root_folder, fdm_tmp_folder


class FDMInterface(object):
    def __init__(self, fdm_path=None, table_path=None, tmp_path=None):
        self._fdm_path = fdm_path
        if fdm_path is None:
            # self._fdm_path = r"D:\JWork\Agents\workspace\UAM_Workflows\FlightDynamics\new_fdm.exe"
            self._fdm_path = fdm_bin_folder / "new_fdm.exe"

        self._table_path = table_path
        if table_path is None:
            # self._table_path = r"D:\JWork\Agents\workspace\UAM_Workflows\Tables\PropData"
            self._table_path = fdm_root_folder / "Tables" / "PropData"

        self._tmp_path = tmp_path
        if tmp_path is None:
            # self._tmp_path = os.path.join(os.path.dirname(__file__), "..", "fdm")
            # self._tmp_path = os.path.join(os.path.dirname(__file__), "..", "fdm")
            self._tmp_path = fdm_tmp_folder

    def execute_from_data(self, fdm_data, fdm_args=None):
        """execute the fdm with the data.
        If fdm_args is provided, data will be changed"""
        if fdm_args is not None:
            self.set_fdm_Data(fdm_data, fdm_args)
        # print(fdm_data.data)
        inp_file_path = os.path.join(self._tmp_path, "tmp.inp")
        out_file_path = os.path.join(self._tmp_path, "tmp.out")
        fdm_data.write_input(inp_file_path)
        return self.executeFDM(inp_file_path, out_file_path)

    def execute_from_file(self, file_name, fdm_args):
        fdm_data = FDMData(self._table_path, file_name)
        self.set_fdm_Data(fdm_data, fdm_args)
        return self.execute_from_data(fdm_data)

    def set_fdm_Data(self, fdm_data, fdm_args):
        # set the arguments into the data
        for arg_name, val in fdm_args.args.items():
            if arg_name in fdm_data.data.keys():
                fdm_data.data[arg_name] = val
            else:
                print(arg_name, fdm_data.data.keys())
                raise Exception(f"Cannot set new argument in the fdm data: {arg_name}")

    def executeFDM(self, inp_path, out_path):
        cmd = "{} <{}> {}".format(self._fdm_path, inp_path, out_path)
        # print(cmd)
        status = os.system(cmd)
        if status != 0:
            print("FDM execution error!")
            raise Exception()
        return FDMResult(out_path)

    def getFDMArgs(self, **kwargs):
        return FDMArgs(**kwargs)

    def read_fdm_input(self, file_path):
        return FDMData(self._table_path, file_path)


class FDMArgs:
    def __init__(self, fdm_data, **kwargs):
        if fdm_data is None:
            self._kwargs = {
                "i_flight_path": 1,
                "requested_lateral_speed": 8,
                "requested_vertical_speed": 0,
                "Q_position": 1.0,
                "Q_velocity": 1.0,
                "Q_angular_velocity": 0.0,
                "Q_angles": 1.0,
                "R": 1.0,
            }
        else:
            self._kwargs = {
                "i_flight_path": fdm_data.data["i_flight_path"],
                "requested_lateral_speed": fdm_data.data["requested_lateral_speed"],
                "requested_vertical_speed": fdm_data.data["requested_vertical_speed"],
                "Q_position": fdm_data.data["Q_position"],
                "Q_velocity": fdm_data.data["Q_velocity"],
                "Q_angular_velocity": fdm_data.data["Q_angular_velocity"],
                "Q_angles": fdm_data.data["Q_angles"],
                "R": fdm_data.data["R"],
            }
        for key, val in kwargs.items():
            self.set_args(key, val)

    @property
    def args(self):
        return self._kwargs

    @property
    def var_names(self):
        return self._kwargs.keys()

    def set_args(self, name, val):
        if name not in self._kwargs.keys():
            raise Exception(f"New Key not allowed: {name}")
        self._kwargs[name] = val

    def get_args(self, name):
        if name not in self._kwargs.keys():
            raise Exception("Key does not exist in FMD Arguments")
        return self._kwargs[name]


# class TrimStateResult():

# 	def __init__(self):

# 	def get


if __name__ == "__main__":
    fdm_interface = FDMInterface()
    file_path = os.path.join(os.path.dirname(__file__), "..", "fdm", "Trowel", "flightDyn.inp")
    data = fdm_interface.read_fdm_input(file_path)

    for i in [1, 3, 4, 5]:
        fdm_args = FDMArgs(data, **{"i_flight_path": i})
        fdm_output = fdm_interface.execute_from_data(data, fdm_args)
        # print(i, fdm_output.metrics)
        print(fdm_output.fastest_trim_state)
