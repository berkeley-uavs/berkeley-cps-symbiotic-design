import math

from sym_cps.contract.tool.contract_tool import ContractManager, ContractTemplate
from sym_cps.representation.library.elements.library_component import LibraryComponent

class UAVContract(object):
    def __init__(self, num_motor, num_battery):
        self._contracts = {}
        self._num_motor = num_motor
        self._num_battery = num_battery
        self.set_contract()


    def set_contract(self):

        propeller_port_name_list = ["rho", "omega_prop", "torque_prop", "thrust", "shaft_motor"]
        propeller_property_name_list = ["C_p", "C_t", "diameter", "shaft_prop", "W_prop"]

        def propeller_assumption(vs):
            return [vs["shaft_prop"] >= vs["shaft_motor"], vs["C_p"] >= 0]

        def propeller_guarantee(vs):
            return [
                vs["torque_prop"]
                == vs["C_p"] * vs["rho"] * vs["omega_prop"] ** 2 * vs["diameter"] ** 5 / (2 * 3.14159265) ** 3,
                vs["thrust"]
                == (vs["C_t"] * vs["rho"] * vs["omega_prop"] ** 2 * vs["diameter"] ** 4 / (2 * 3.14159265) ** 2),
                vs["omega_prop"] >= 0,
            ]

        propeller_contract = ContractTemplate(
            name="Propeller",
            port_name_list=propeller_port_name_list,
            property_name_list=propeller_property_name_list,
            guarantee=propeller_guarantee,
            assumption=propeller_assumption,
        )
        self._contracts["Propeller"] = propeller_contract

        motor_port_name_list = ["torque_motor", "omega_motor", "I_motor", "V_motor"]
        motor_property_name_list = [
            "I_max_motor",
            "P_max_motor",
            "K_t",
            "K_v",
            "W_motor",
            "R_w",
            "I_idle",
            "shaft_motor",
        ]

        def motor_assumption(vs):
            return [vs["V_motor"] * vs["I_motor"] < vs["P_max_motor"], vs["I_motor"] < vs["I_max_motor"]]

        def motor_guarantee(vs):
            return [
                vs["I_motor"] * vs["R_w"] == vs["V_motor"] - vs["omega_motor"] / vs["K_v"],
                vs["torque_motor"]
                == vs["K_t"] / vs["R_w"] * (vs["V_motor"] - vs["R_w"] * vs["I_idle"] - vs["omega_motor"] / vs["K_v"]),
            ]

        motor_contract = ContractTemplate(
            name="Motor",
            port_name_list=motor_port_name_list,
            property_name_list=motor_property_name_list,
            guarantee=motor_guarantee,
            assumption=motor_assumption,
        )
        self._contracts["Motor"] = motor_contract

        battery_port_name_list = ["I_batt"]
        battery_property_name_list = ["capacity", "W_batt", "I_max", "V_battery"]

        def battery_assumption(vs):
            return [vs["I_batt"] < vs["I_max"]]

        def battery_guarantee(vs):
            return []

        battery_contract = ContractTemplate(
            name="Battery",
            port_name_list=battery_port_name_list,
            property_name_list=battery_property_name_list,
            guarantee=battery_guarantee,
            assumption=battery_assumption,
        )

        self._contracts["Battery"] = battery_contract

        battery_controller_port_name_list = ["V_battery", "I_battery"]
        battery_controller_property_name_list = [f"I_motor_{i}" for i in range(self._num_motor)] + [
            f"V_motor_{i}" for i in range(self._num_motor)
        ]

        def battery_controller_assumption(vs):
            return [vs[f"V_motor_{i}"] <= vs["V_battery"] for i in range(self._num_motor)]

        def battery_controller_guarantee(vs):
            i_sum = sum([vs[f"I_motor_{i}"] for i in range(self._num_motor)])
            return [i_sum == vs["I_battery"] * 0.95]

        battery_controller_contract = ContractTemplate(
            name="BatteryController",
            port_name_list=battery_controller_port_name_list,
            property_name_list=battery_controller_property_name_list,
            guarantee=battery_controller_guarantee,
            assumption=battery_controller_assumption,
        )

        self._contracts["BatteryController"] = battery_controller_contract

        # system contract

    @staticmethod
    def hackathon_property_interface_fn(component: LibraryComponent):
        if component.comp_type.id == "Propeller":
            return UAVContract.hackthon_get_propeller_property(propeller=component, table_dict=self._table_dict)
        elif component.comp_type.id == "Battery":
            return UAVContract.hackthon_get_battery_property(battery=component, num_battery=self._num_battery)
        elif component.comp_type.id == "Motor":
            return UAVContract.hackthon_get_motor_property(motor=component)
        elif component.comp_type.id == "BatteryController":
            return {}

    @staticmethod
    def hackthon_get_propeller_property(propeller, table_dict):
        # ports get value

        diameter: float = propeller.properties["DIAMETER"].value / 1000
        shaft_prop: float = propeller.properties["SHAFT_DIAMETER"].value
        # print(table.get_value(rpm = 13000, v = 90, label="Cp"))
        table = table_dict[propeller]
        C_p: float = table.get_value(rpm=10000, v=0, label="Cp")  # 0.0659
        C_t: float = table.get_value(rpm=10000, v=0, label="Ct")  # 0.1319

        W_prop = propeller.properties["WEIGHT"].value
        return {
            "C_p": C_p,
            "C_t": C_t,
            "W_prop": W_prop,
            "diameter": diameter,
            "shaft_prop": shaft_prop,
            "name": propeller.id,
        }

    @staticmethod
    def hackthon_get_motor_property(motor):
        R_w: float = motor.properties["INTERNAL_RESISTANCE"].value / 1000  # Ohm
        K_t: float = motor.properties["KT"].value
        K_v: float = motor.properties["KV"].value * (2 * math.pi) / 60  # rpm/V to rad/(V-sec)
        I_idle: float = motor.properties["IO_IDLE_CURRENT_10V"].value
        W_motor = motor.properties["WEIGHT"].value
        I_max_motor = motor.properties["MAX_CURRENT"].value
        P_max_motor = motor.properties["MAX_POWER"].value
        shaft__motor: float = motor.properties["SHAFT_DIAMETER"].value
        return {
            "R_w": R_w,
            "K_t": K_t,
            "K_v": K_v,
            "I_idle": I_idle,
            "W_motor": W_motor,
            "I_max_motor": I_max_motor,
            "P_max_motor": P_max_motor,
            "shaft_motor": shaft__motor,
            "name": motor.id,
        }

    @staticmethod
    def hackthon_get_battery_property(battery, num_battery):
        capacity: float = battery.properties["CAPACITY"].value * num_battery / 1000  # mAh -> Ah
        W_batt: float = battery.properties["WEIGHT"].value * num_battery
        V_battery: float = battery.properties["VOLTAGE"].value
        I_max: float = (battery.properties["CONT_DISCHARGE_RATE"].value) * capacity  # convert to mA
        return {"capacity": capacity, "W_batt": W_batt, "V_battery": V_battery, "I_max": I_max, "name": battery.id}