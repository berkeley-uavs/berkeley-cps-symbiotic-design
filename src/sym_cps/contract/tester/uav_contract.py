import math

from sym_cps.contract.tool.component_interface import ComponentInterface
from sym_cps.contract.tool.contract_template import ContractTemplate
from sym_cps.representation.library.elements.library_component import LibraryComponent


class UAVContract(object):
    def __init__(self, table_dict: dict, num_motor=None, num_battery=None):
        self._contracts = {}
        self._table_dict = table_dict
        self.set_num(num_motor=num_motor, num_battery=num_battery)
        # self.set_contract()
        self._rpm_static = 10000
        self._rpm_upper = 18000
        self._speed = 1
        self._speed_upper = 50

    def get_contract(self, contract_name: str) -> ContractTemplate:
        return self._contracts[contract_name]

    def set_num(self, num_motor, num_battery):
        self._num_motor = num_motor
        self._num_battery = num_battery

    def build_components_from_library_component(self, components: list[LibraryComponent]):
        """Interface for creating list of components for contract tools from Library Component"""
        ret_components = []
        for comp in components:
            prop_dict = self._hackathon_property_interface_fn(comp)
            ret_components.append(prop_dict)
        return ret_components

    def add_battery(self):
        battery_port_list = [ComponentInterface(name="I_batt", sort="real")]
        battery_property_list = [
            ComponentInterface(name="capacity", sort="real"),
            ComponentInterface(name="W_batt", sort="real"),
            ComponentInterface(name="I_max", sort="real"),
            ComponentInterface(name="V_battery", sort="real"),
        ]

        def battery_assumption(vs):
            return [vs["I_batt"] <= vs["I_max"]]

        def battery_guarantee(vs):
            return []

        battery_contract = ContractTemplate(
            name="Battery",
            port_list=battery_port_list,
            property_list=battery_property_list,
            guarantee=battery_guarantee,
            assumption=battery_assumption,
        )
        self._contracts["Battery"] = battery_contract

    def add_motor(self):
        motor_port_list = [
            ComponentInterface(name="torque_motor", sort="real"),
            ComponentInterface(name="omega_motor", sort="real"),
            ComponentInterface(name="I_motor", sort="real"),
            ComponentInterface(name="V_motor", sort="real"),
        ]
        motor_property_list = [
            ComponentInterface(name="I_max_motor", sort="real"),
            ComponentInterface(name="P_max_motor", sort="real"),
            ComponentInterface(name="K_t", sort="real"),
            ComponentInterface(name="K_v", sort="real"),
            ComponentInterface(name="W_motor", sort="real"),
            ComponentInterface(name="R_w", sort="real"),
            ComponentInterface(name="I_idle", sort="real"),
            ComponentInterface(name="shaft_motor", sort="real"),
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
            port_list=motor_port_list,
            property_list=motor_property_list,
            guarantee=motor_guarantee,
            assumption=motor_assumption,
        )
        self._contracts["Motor"] = motor_contract

    def add_propeller_simplified(self, propeller_direction: list):
        """Propeller direction is used for considering those propeller not complete contributing to upward thrust
        1.0 means full facing up. other number means the ratio that the thrust is used for thrust
        """
        thrust_multiplier = sum(propeller_direction)
        propeller_port_list = [
            ComponentInterface(name="rho", sort="real"),
            ComponentInterface(name="omega_prop", sort="real"),
            ComponentInterface(name="torque_prop", sort="real"),
            ComponentInterface(name="thrust", sort="real"),
            ComponentInterface(name="shaft_motor", sort="real"),
        ]
        propeller_property_list = [
            ComponentInterface(name="C_p", sort="real"),
            ComponentInterface(name="C_t", sort="real"),
            ComponentInterface(name="diameter", sort="real"),
            ComponentInterface(name="shaft_prop", sort="real"),
            ComponentInterface(name="W_prop", sort="real"),
        ]

        def propeller_assumption(vs):
            return [vs["shaft_prop"] >= vs["shaft_motor"], vs["C_p"] >= 0]

        def propeller_guarantee(vs):
            return [
                vs["torque_prop"]
                == vs["C_p"] * vs["rho"] * vs["omega_prop"] ** 2 * vs["diameter"] ** 5 / (2 * 3.14159265) ** 3,
                vs["thrust"]
                == (vs["C_t"] * vs["rho"] * vs["omega_prop"] ** 2 * vs["diameter"] ** 4 / (2 * 3.14159265) ** 2)
                * thrust_multiplier,
                vs["omega_prop"] >= 0,
            ]

        propeller_contract = ContractTemplate(
            name="Propeller",
            port_list=propeller_port_list,
            property_list=propeller_property_list,
            guarantee=propeller_guarantee,
            assumption=propeller_assumption,
        )
        self._contracts["Propeller"] = propeller_contract

    def add_propeller(self, upward_ratio=1.0):
        propeller_port_list = [
            ComponentInterface(name="rho", sort="real"),
            ComponentInterface(name="omega_prop", sort="real"),
            ComponentInterface(name="torque_prop", sort="real"),
            ComponentInterface(name="thrust", sort="real"),
            ComponentInterface(name="shaft_motor", sort="real"),
        ]
        propeller_property_list = [
            ComponentInterface(name="C_p", sort="real"),
            ComponentInterface(name="C_t", sort="real"),
            ComponentInterface(name="diameter", sort="real"),
            ComponentInterface(name="shaft_prop", sort="real"),
            ComponentInterface(name="W_prop", sort="real"),
        ]

        def propeller_assumption(vs):
            return [vs["shaft_prop"] >= vs["shaft_motor"], vs["C_p"] >= 0]

        def propeller_guarantee(vs):
            return [
                vs["torque_prop"]
                == vs["C_p"] * vs["rho"] * vs["omega_prop"] ** 2 * vs["diameter"] ** 5 / (2 * 3.14159265) ** 3,
                vs["thrust"]
                == (vs["C_t"] * vs["rho"] * vs["omega_prop"] ** 2 * vs["diameter"] ** 4 / (2 * 3.14159265) ** 2)
                * upward_ratio,
                vs["omega_prop"] >= 0,
            ]

        propeller_contract = ContractTemplate(
            name="Propeller",
            port_list=propeller_port_list,
            property_list=propeller_property_list,
            guarantee=propeller_guarantee,
            assumption=propeller_assumption,
        )
        self._contracts["Propeller"] = propeller_contract

    def add_battery_controller_simplified(self):
        battery_controller_port_list = [
            ComponentInterface(name="V_battery", sort="real"),
            ComponentInterface(name="I_battery", sort="real"),
            ComponentInterface(name="V_motor", sort="real"),
            ComponentInterface(name="I_motor", sort="real"),
        ]
        battery_controller_property_list = []

        def battery_controller_assumption(vs):
            return [vs["V_motor"] <= vs["V_battery"]]

        def battery_controller_guarantee(vs):
            return [vs["I_motor"] * self._num_motor == vs["I_battery"] * 0.95]

        battery_controller_contract = ContractTemplate(
            name="BatteryController",
            port_list=battery_controller_port_list,
            property_list=battery_controller_property_list,
            guarantee=battery_controller_guarantee,
            assumption=battery_controller_assumption,
        )
        self._contracts["BatteryController"] = battery_controller_contract

    def add_battery_controller(self):
        battery_controller_port_list = (
            [ComponentInterface(name="V_battery", sort="real"), ComponentInterface(name="I_battery", sort="real")]
            + [ComponentInterface(name=f"I_motor_{i}", sort="real") for i in range(self._num_motor)]
            + [ComponentInterface(name=f"V_motor_{i}", sort="real") for i in range(self._num_motor)]
        )

        battery_controller_property_list = []

        def battery_controller_assumption(vs):
            return [vs[f"V_motor_{i}"] <= vs["V_battery"] for i in range(self._num_motor)]

        def battery_controller_guarantee(vs):
            i_sum = sum([vs[f"I_motor_{i}"] for i in range(self._num_motor)])
            return [i_sum == vs["I_battery"] * 0.95]

        battery_controller_contract = ContractTemplate(
            name="BatteryController",
            port_list=battery_controller_port_list,
            property_list=battery_controller_property_list,
            guarantee=battery_controller_guarantee,
            assumption=battery_controller_assumption,
        )
        self._contracts["BatteryController"] = battery_controller_contract

    def set_contract(self):
        self.add_battery()
        self.add_motor()
        self.add_battery_controller()
        self.add_propeller()

    def set_contract_simplified(self, propeller_direction: list = None):
        if propeller_direction is None:
            propeller_direction = [1.0] * self._num_motor
        if len(propeller_direction) != self._num_motor:
            print("The direction list does not match the number of motors!")
            return

        self.add_battery()
        self.add_motor()
        self.add_battery_controller_simplified()
        self.add_propeller_simplified(propeller_direction=propeller_direction)

        # system contract

    def hackathon_property_interface_fn(self, component: LibraryComponent, use_rpm_v_range: bool = False):
        if component.comp_type.id == "Propeller":
            return self.hackthon_get_propeller_property(
                propeller=component,
                table_dict=self._table_dict,
                rpm=self._rpm_static,
                rpm2=self._rpm_upper,
                v=self._speed,
                v2=self._speed_upper,
                num_motor=1,
                use_rpm_v_range=use_rpm_v_range,
            )
        elif component.comp_type.id == "Battery":
            return self.hackthon_get_battery_property(battery=component, num_battery=self._num_battery)
        elif component.comp_type.id == "Motor":
            return self.hackthon_get_motor_property(motor=component, num_motor=1)
        elif component.comp_type.id == "BatteryController":
            return {}

    def hackathon_property_interface_fn_aggregated(self, component: LibraryComponent, use_rpm_v_range: bool = False):
        if component.comp_type.id == "Propeller":
            return self.hackthon_get_propeller_property(
                propeller=component,
                table_dict=self._table_dict,
                rpm=self._rpm_static,
                rpm2=self._rpm_upper,
                v=self._speed,
                v2=self._speed_upper,
                num_motor=self._num_motor,
                use_rpm_v_range=use_rpm_v_range,
            )
        elif component.comp_type.id == "Battery":
            return self.hackthon_get_battery_property(battery=component, num_battery=self._num_battery)
        elif component.comp_type.id == "Motor":
            return self.hackthon_get_motor_property(motor=component, num_motor=self._num_motor)
        elif component.comp_type.id == "BatteryController":
            return {}

    def hackthon_get_propeller_property(self, propeller, table_dict, rpm, rpm2, v, v2, num_motor, use_rpm_v_range):
        # ports get value

        diameter: float = propeller.properties["DIAMETER"].value / 1000
        shaft_prop: float = propeller.properties["SHAFT_DIAMETER"].value
        # print(table.get_value(rpm = 13000, v = 90, label="Cp"))
        table = table_dict[propeller]
        if not use_rpm_v_range:
            C_p: float = table.get_value(rpm=rpm, v=v, label="Cp")  # 0.0659
            C_t: float = table.get_value(rpm=rpm, v=v, label="Ct")  # 0.1319
        else:
            C_p: tuple[float, float] = table.get_range(rpm1=rpm, rpm2=rpm2, v1=v, v2=v2, label="Cp")
            C_t: tuple[float, float] = table.get_range(rpm1=rpm, rpm2=rpm2, v1=v, v2=v2, label="Ct")

        W_prop = propeller.properties["WEIGHT"].value * num_motor
        return {
            "C_p": C_p,
            "C_t": C_t,
            "W_prop": W_prop,
            "diameter": diameter,
            "shaft_prop": shaft_prop,
            "name": propeller.id,
        }

    def hackthon_get_motor_property(self, motor, num_motor):
        R_w: float = motor.properties["INTERNAL_RESISTANCE"].value / 1000  # Ohm
        K_t: float = motor.properties["KT"].value
        K_v: float = motor.properties["KV"].value * (2 * math.pi) / 60  # rpm/V to rad/(V-sec)
        I_idle: float = motor.properties["IO_IDLE_CURRENT_10V"].value
        W_motor = motor.properties["WEIGHT"].value * num_motor
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

    def hackthon_get_battery_property(self, battery, num_battery):
        capacity: float = battery.properties["CAPACITY"].value * num_battery / 1000  # mAh -> Ah
        W_batt: float = battery.properties["WEIGHT"].value * num_battery
        V_battery: float = battery.properties["VOLTAGE"].value
        I_max: float = (battery.properties["CONT_DISCHARGE_RATE"].value) * capacity  # convert to mA
        return {"capacity": capacity, "W_batt": W_batt, "V_battery": V_battery, "I_max": I_max, "name": battery.id}

    def set_rpm(self, rpm):
        self._rpm_static = rpm

    def set_rpm_upper(self, rpm):
        self._rpm_upper = rpm

    def set_speed_upper(self, v):
        self._speed_upper = v

    def set_speed(self, v):
        self._speed = v
