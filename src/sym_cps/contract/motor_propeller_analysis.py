import math

from sym_cps.contract.tool.contract_tool import ContractManager, ContractTemplate
from sym_cps.representation.library.elements.library_component import LibraryComponent

class MotorPropellerAnalysis(object):
    def __init__(self, table_dict, c_library):
        self._table_dict = table_dict
        self._c_library = c_library
        ret = []
        for prop in self._c_library.components_in_type["Propeller"]:
            for motor in self._c_library.components_in_type["Motor"]:
                print(f"Analyze ({prop.id}, {motor.id})", end="")
                self.analysis(add_weight=0, motors=[motor], propellers=[prop])
                is_sat = self._manager.solve()
                if is_sat:
                    ret.append((prop, motor))
                    print("     OK")
                else: 
                    print("     Incompatible")
        print(len(ret))
                    



    def analysis(self, 
                add_weight = 0,
                motors: list[LibraryComponent] = None,
                propellers: list[LibraryComponent] = None):

        """Analyze requirement for motor and propeller"""
        if propellers is None:
            propellers = list(self._c_library.components_in_type["Propeller"])
            #propellers = [self._c_library.components["apc_propellers_6x4E"]]

            # propellers = [[self._c_library.components["apc_propellers_6x4E"],
            #                self._c_library.components["apc_propellers_15x6E"],
            #                self._c_library.components["apc_propellers_26x15E"]] ] * num_motor
        if motors is None:
            motors = list(self._c_library.components_in_type["Motor"])
            #motors = [self._c_library.components["t_motor_AT2312KV1400"]]
            #             self._c_library.components["t_motor_AntigravityMN4006KV380"],
            #             self._c_library.components["t_motor_AntigravityMN1005V2KV90"]
        self.set_contract()
        self.set_system(add_weight=add_weight)
        self._manager = ContractManager(self.hackathon_property_interface_fn, verbose=False)

        motor_inst = self._contracts["Motor"].instantiate(f"MotorInst")
        prop_inst = self._contracts["Propeller"].instantiate(f"PropellerInst")
        system_inst = self._contracts["System"].instantiate(f"System")
        self._manager.add_instance(motor_inst)
        self._manager.add_instance(prop_inst)
        self._manager.add_instance(system_inst)
        self._manager.set_selection(inst=prop_inst, candidate_list=propellers)
        self._manager.set_selection(inst=motor_inst, candidate_list=motors)

        propeller_motor_connection = [
            ("torque_prop", "torque_motor"),
            ("omega_prop", "omega_motor"),
            ("shaft_motor", "shaft_motor"),
        ]
        self._manager.compose(prop_inst, motor_inst, propeller_motor_connection)

        system_prop_connection = [("W_prop", "W_prop"), ("thrust", f"thrust"), ("rho", "rho")]
        self._manager.compose(system_inst, prop_inst, system_prop_connection)
        system_motor_connection = [(f"W_motor", f"W_motor"), ("I_motor", "I_motor"), ("V_motor", "V_motor")]
        self._manager.compose(system_inst, motor_inst, system_motor_connection)

        objective_expr = system_inst.get_var("thrust") - system_inst.get_var("weight_sum")
        objective_val = -100

        def objective_fn():
            thrust_sum = self._manager.get_metric_inst(system_inst, "thrust")
            weight_sum = self._manager.get_metric_inst(system_inst, "weight_sum")
            return thrust_sum - weight_sum

        self._manager.set_objective(expr=objective_expr, value=objective_val, evaluate_fn=objective_fn)
    def set_system(self, add_weight = 0):
        system_port_name_list = ["rho", "thrust", "weight_sum", "I_motor", "W_motor", "W_prop", "thrust", "V_motor"]
        system_property_name_list = []

        def system_assumption(vs):
            return [vs["I_motor"] <= 5]

        def system_guarantee(vs):
            weight_sum = (
                add_weight
                + vs["W_prop"]
                + vs["W_motor"]
            ) * 9.81
            ret_clauses = [ vs["weight_sum"] == weight_sum,
                           vs["rho"] == 1.225,
                           vs["thrust"] >= vs["weight_sum"]
                           vs["V_motor"] <= 7]

            return ret_clauses

        system_contract = ContractTemplate(
            name="System",
            port_name_list=system_port_name_list,
            property_name_list=system_property_name_list,
            guarantee=system_guarantee,
            assumption=system_assumption,
        )
        self._contracts["System"] = system_contract

    def set_contract(self):
        self._contracts = {}

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

        # system contract

    def hackathon_property_interface_fn(self, component: LibraryComponent):
        if component.comp_type.id == "Propeller":
            return self.hackthon_get_propeller_property(propeller=component, table_dict=self._table_dict)
        elif component.comp_type.id == "Battery":
            return self.hackthon_get_battery_property(battery=component, num_battery=self._num_battery)
        elif component.comp_type.id == "Motor":
            return self.hackthon_get_motor_property(motor=component)
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

if __name__ == "__main__":
    from sym_cps.representation.tools.parsers.parse import parse_library_and_seed_designs
    from sym_cps.representation.tools.parsers.parsing_prop_table import parsing_prop_table
    c_library, designs = parse_library_and_seed_designs()
    table_dict = parsing_prop_table(c_library)
    MotorPropellerAnalysis(table_dict=table_dict, c_library=c_library)