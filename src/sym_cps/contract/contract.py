
from typing import TYPE_CHECKING
from sym_cps.representation.library import Library
import z3
from sym_cps.representation.library.elements.c_type import CType
import math
if TYPE_CHECKING:
    from sym_cps.representation.library.elements.c_type import CType


class Contract():
    def __init__(self, name, vs: list[str], assumption, guarantee):
        """Assumption should be a function that returns assumption constraint using the input vs"""
        self._assumption = assumption
        self._guarantee = guarantee
        self._name = name
        self._count = 0
        self._vs = vs

    def instantiate(self, instance_name = ""):
        """Instantiate a contract"""
        self._count += 1
        vs = {v: z3.Real(f"{v}_{self._name}_{instance_name}_{self._count}") for v in self._vs}
        A = self._assumption(vs)
        G = self._guarantee(vs)
        return vs, A, G

class ContractManager():
    def __init__(self):
        self._all_vs = {}
        self._vs_dict = {}
        self._clauses = []
        self._contracts = {}

    @staticmethod
    def hackthon_get_propeller_property( propeller, table_dict, num_motor):
        # ports get value

        diameter: float = propeller.properties["DIAMETER"].value / 1000
        shaft_prop: float = propeller.properties["SHAFT_DIAMETER"].value
        #print(table.get_value(rpm = 13000, v = 90, label="Cp"))
        table = table_dict[propeller]
        C_p: float = table.get_value(rpm = 10000, v = 0, label="Cp")#0.0659 
        C_t: float = table.get_value(rpm = 10000, v = 0, label="Ct")#0.1319

        W_prop = propeller.properties["Weight"].value * num_motor
        return {"C_p": C_p,
                "C_t": C_t,
                "W_prop": W_prop,
                "diameter": diameter,
                "shaft_prop": shaft_prop}


    @staticmethod
    def hackthon_get_motor_property(motor, num_motor):
        R_w : float = motor.properties["INTERNAL_RESISTANCE"].value / 1000 # Ohm
        K_t : float = motor.properties["KT"].value
        K_v : float = motor.properties["KV"].value * (2 * math.pi)/60 # rpm/V to rad/(V-sec)
        I_idle : float = motor.properties["IO_IDLE_CURRENT_10V"].value
        W_motor = motor.properties["WEIGHT"].value * num_motor
        I_max_motor = motor.properties["MAX_CURRENT"].value
        P_max_motor = motor.properties["MAX_POWER"].value
        shaft__motor: float = motor.properties["SHAFT_DIAMETER"].value
        return {"R_w": R_w,
                "K_t": K_t,
                "K_v": K_v,
                "I_idle": I_idle,
                "W_motor": W_motor,
                "I_max_motor": I_max_motor,
                "P_max_motor": P_max_motor,
                "shaft_motor": shaft__motor}

    @staticmethod
    def hackthon_get_battery_property(battery, num_battery):
        capacity: float = battery.properties["CAPACITY"].value * num_battery / 1000# mAh -> Ah
        W_batt: float = battery.properties["WEIGHT"].value * num_battery
        V_battery: float = battery.properties["VOLTAGE"].value
        I_max: float = (battery.properties["CONT_DISCHARGE_RATE"].value) * capacity# convert to mA
        return {"capacity": capacity,
                "W_batt": W_batt,
                "V_battery": V_battery,
                "I_max": I_max}

    def check_selection(self, num_battery, num_motor, c_library, table_dict, battery, motor, propeller):
        self.hackathon_compose(num_battery=num_battery, 
            num_motor=num_motor, 
            c_library=c_library, 
            table_dict=table_dict, 
            batteries=[battery],
            motors=[motor],
            propellers=[propeller])
        objective = self.solve(c_library)
        print("Check Completed")
        return objective


    def hackathon_contract(self, num_battery, num_motor):
        """Hardcoded for Hackathon
        Simplified version: use the same component for the whole system"""
        self._contracts = {}
        def motor_assumtion(vs):
            return [vs["V_motor"] * vs["I_motor"] < vs["P_max_motor"], vs["I_motor"] < vs["I_max_motor"]]
        def motor_guarantee(vs):
            return [vs["I_motor"] * vs["R_w"] == vs["V_motor"] - vs["omega_motor"] / vs["K_v"], 
                    vs["torque_motor"] == vs["K_t"]/vs["R_w"] * (vs["V_motor"] - vs["R_w"] * vs["I_idle"] - vs["omega_motor"]/vs["K_v"])]
        motor_name_list = ["torque_motor", "omega_motor", "I_motor", "V_motor", "P_max_motor",
                            "I_max_motor", "K_t", "K_v", "W_motor", "R_w", "I_idle", "shaft_motor"]
        motor_contract = Contract("motor", motor_name_list, motor_assumtion, motor_guarantee)
        self._contracts["motor"] = motor_contract

        def propeller_assumption(vs):
            return [vs["shaft_prop"] >= vs["shaft_motor"], vs["C_p"] >= 0]
        def propeller_guarantee(vs):
            return [vs["torque_prop"] == vs["C_p"] * vs["rho"] * vs["omega_prop"]**2 * vs["diameter"] ** 5 / (2 * 3.14159265) ** 3,
                    vs["thrust"] == (vs["C_t"] * vs["rho"] * vs["omega_prop"]**2 * vs["diameter"] ** 4 / (2 * 3.14159265) ** 2) * num_motor,
                    vs["omega_prop"] >= 0]
        propeller_name_list = ["C_p", "C_t", "rho", "W_prop", "omega_prop", "torque_prop", "diameter", "thrust", "shaft_motor", "shaft_prop"]
        propeller_contract = Contract("propeller", propeller_name_list, propeller_assumption, propeller_guarantee)
        
        self._contracts["propeller"] = propeller_contract


        def battery_assumption(vs):
            return [vs["I_batt"] < vs["I_max"]]
        def battery_guarantee(vs):
            return []
        battery_name_list = ["capacity", "W_batt", "I_batt", "I_max", "V_battery"]
        battery_contract = Contract("battery", battery_name_list, battery_assumption, battery_guarantee)
        
        self._contracts["battery"] = battery_contract

        def battery_controller_assumption(vs):
            return [ vs["V_motor"] <= vs["V_battery"] ]
        def battery_controller_guarantee(vs):
            return [ vs["I_motor"] * num_motor == vs["I_battery"] * 0.95]
        battery_controller_name_list = ["capacity", "V_battery", "I_battery", "V_motor", "I_motor"]
        battery_controller_contract = Contract("batt_controller", battery_controller_name_list, battery_controller_assumption, battery_controller_guarantee)
        
        self._contracts["battery_controller"] = battery_controller_contract

        def system_assumption(vs):
            return []
        def system_guarantee(vs):
            return [vs["thrust_sum"] >= vs["weight_sum"], vs["rho"] == 1.225]
        system_name_list = ["thrust_sum", "weight_sum", "rho"]
        system_contract = Contract("system", system_name_list, system_assumption, system_guarantee)
        self._contracts["system"] = system_contract
        return self._contracts

    def hackathon_compose(self, num_battery, 
                                num_motor, 
                                c_library, 
                                table_dict, 
                                better_selection_encoding = True, 
                                batteries = None, 
                                motors = None, 
                                propellers = None,
                                obj_lower_bound = None):
        if propellers is None:
            propellers = c_library.components_in_type["Propeller"]
        if motors is None:
            motors = c_library.components_in_type["Motor"]
        if batteries is None:
            batteries = c_library.components_in_type["Battery_UAV"]
        """Form the OMT problem"""
        #self._all_vs = {}
        self._all_clause = []

        print("Generate Propeller Contract")
        prop_vs, A, G = self._contracts["propeller"].instantiate()
        self._vs_dict["propeller"] = prop_vs
        #self._all_vs.update(prop_vs)
        self._all_clause.extend(A)
        self._all_clause.extend(G)

        print("Generate Motor Contract")
        motor_vs, A, G = self._contracts["motor"].instantiate()
        self._vs_dict["motor"] = motor_vs
        #self._all_vs.update(motor_vs)
        self._all_clause.extend(A)
        self._all_clause.extend(G)
        # connect motor with propeller
        # should follow the connection
        self._all_clause.append(prop_vs["torque_prop"] == motor_vs["torque_motor"])
        self._all_clause.append(prop_vs["omega_prop"] == motor_vs["omega_motor"])
        self._all_clause.append(prop_vs["shaft_motor"] == motor_vs["shaft_motor"])
        # connection motor with battery controller
        print("Generate Battery Controller Contract")
        contr_vs, A, G  = self._contracts["battery_controller"].instantiate()
        self._vs_dict["battery_controller"] = contr_vs
        #self._all_vs.update(contr_vs)
        self._all_clause.extend(A)
        self._all_clause.extend(G)
        self._all_clause.append(contr_vs["I_motor"] == motor_vs["I_motor"])
        self._all_clause.append(contr_vs["V_motor"] == motor_vs["V_motor"])
        
        # connect controller to battery
        print("Generate Battery Contract")
        battery_vs, A, G = self._contracts["battery"].instantiate()
        self._vs_dict["battery"] = battery_vs
        #self._all_vs.update(battery_vs)
        self._all_clause.extend(A)
        self._all_clause.extend(G)
        self._all_clause.append(battery_vs["I_batt"] == contr_vs["I_battery"])
        self._all_clause.append(battery_vs["V_battery"] == contr_vs["V_battery"])
        

        # selection of all battery
        prop_select_vs = {}
        print("Generate Propeller Selection Property")
        for n_p, propeller in enumerate(propellers): #enumerate([c_library.components["apc_propellers_22x12WE"]]):#
            if propeller.properties["SHAFT_DIAMETER"].value >= 30:
                continue
            use_v = z3.Bool(f"use_{propeller.id}")
            prop_select_vs.update({f"{propeller.id}": use_v})
            prop_properties = ContractManager.hackthon_get_propeller_property(propeller=propeller, table_dict=table_dict, num_motor=num_motor)
            self._all_clause.append(z3.Implies(use_v, 
                                         z3.And(prop_vs["C_p"] == prop_properties[f"C_p"], 
                                                prop_vs["C_t"] == prop_properties[f"C_t"],
                                                prop_vs["W_prop"] == prop_properties[f"W_prop"],
                                                prop_vs["diameter"] == prop_properties[f"diameter"],
                                                prop_vs["shaft_prop"] == prop_properties[f"shaft_prop"])))
            # set value
        self._vs_dict["prop_select"] = prop_select_vs
        # can only select one propeller
        print("Generate Rules to Ensure Propeller Selection ")
        for n_p, prop in enumerate(prop_select_vs.values()):
            print(n_p, end="")
            if better_selection_encoding:
                tmp_vs = [prop2 for prop2 in prop_select_vs.values() if prop.get_id() != prop2.get_id()]
                self._all_clause.append(z3.Implies(prop, z3.And(*[z3.Not(prop2) for prop2 in tmp_vs])))      
            else:
                for prop2 in prop_select_vs.values():
                    if prop.get_id() != prop2.get_id():
                        self._all_clause.append(z3.Implies(prop, z3.Not(prop2)))
        # must select one
        self._all_clause.append(z3.Or(*(prop_select_vs.values())))

        motor_select_vs = {}
        print("Generate Motor Selection Property")
        for n_m, motor in enumerate(motors): #enumerate([c_library.components["U8_Lite_KV150"]]):#
            # P_max_motor == P_max_motor_1, W_motor == W_motor_1, I_max_motor == I_max_motor_1,
            #                     K_t == K_t_1, K_v == K_v_1, R_w == R_w_1, I_idle == I_idle_1
            use_v = z3.Bool(f"use_{motor.id}")
            motor_select_vs.update({f"{motor.id}": use_v})

            motor_properties = ContractManager.hackthon_get_motor_property(motor=motor, num_motor=num_motor)
            self._all_clause.append(z3.Implies(use_v, 
                                         z3.And(motor_vs["P_max_motor"] == motor_properties[f"P_max_motor"], 
                                                motor_vs["W_motor"] == motor_properties[f"W_motor"],
                                                motor_vs["I_max_motor"] == motor_properties[f"I_max_motor"],
                                                motor_vs["K_t"] == motor_properties[f"K_t"],
                                                motor_vs["K_v"] == motor_properties[f"K_v"],
                                                motor_vs["R_w"] == motor_properties[f"R_w"],
                                                motor_vs["I_idle"] == motor_properties[f"I_idle"],
                                                motor_vs["shaft_motor"] == motor_properties[f"shaft_motor"])))
        self._vs_dict["motor_select"] = motor_select_vs
        # can only select one motor
        print("Generate Rules to Ensure Motor Selection ")
        for motor in motor_select_vs.values():
            if better_selection_encoding:
                tmp_vs = [motor2 for motor2 in motor_select_vs.values() if motor.get_id() != motor2.get_id()]
                self._all_clause.append(z3.Implies(motor, z3.And(*[z3.Not(motor2) for motor2 in tmp_vs])))                
            else:   
                for motor2 in motor_select_vs.values():
                    if motor.get_id() != motor2.get_id():
                        self._all_clause.append(z3.Implies(motor, z3.Not(motor2)))
        # must select one
        self._all_clause.append(z3.Or(*(motor_select_vs.values())))

        battery_select_vs = {}
        print("Generate Battery Selection Property")
        for n_b, battery in enumerate(batteries): #enumerate([c_library.components["TurnigyGraphene6000mAh6S75C"]]):#
            use_v = z3.Bool(f"use_{battery.id}")
            battery_select_vs.update({f"{battery.id}": use_v})

            battery_properties = ContractManager.hackthon_get_battery_property(battery=battery, num_battery=num_battery)
            self._all_clause.append(z3.Implies(use_v, 
                                         z3.And(battery_vs["capacity"] == battery_properties[f"capacity"], 
                                                battery_vs["W_batt"] == battery_properties[f"W_batt"],
                                                battery_vs["I_max"] == battery_properties[f"I_max"],
                                                battery_vs["V_battery"] == battery_properties[f"V_battery"])))
        self._vs_dict["battery_select"] = battery_select_vs
        # can only select one motor
        print("Generate Rules to Ensure Battery Selection ")
        for battery in battery_select_vs.values():         
            if better_selection_encoding:
                tmp_vs = [battery2 for battery2 in battery_select_vs.values() if battery.get_id() != battery2.get_id()]
                self._all_clause.append(z3.Implies(battery, z3.And(*[z3.Not(battery2) for battery2 in tmp_vs])))   
            else:
                for battery2 in battery_select_vs.values():   
                    if battery.get_id() != battery2.get_id():
                        self._all_clause.append(z3.Implies(battery, z3.Not(battery2)))
        # must select one
        self._all_clause.append(z3.Or(*(battery_select_vs.values())))
        #self._all_vs.update(battery_select_vs)
        #self._all_vs.update(prop_select_vs)
        #self._all_vs.update(motor_select_vs)

        sys_vs, A, G = self._contracts["system"].instantiate()
        #self._all_vs.update(sys_vs)
        self._all_clause.extend(A)
        self._all_clause.extend(G)
        # connect system
        self._all_clause.append(sys_vs["thrust_sum"] == prop_vs["thrust"])
        self._all_clause.append(sys_vs["weight_sum"] == prop_vs["W_prop"] + battery_vs["W_batt"] + motor_vs["W_motor"])
        # tmp for debug
        self._all_clause.append(battery_vs["I_batt"] == battery_vs["capacity"] * 3600 / 400)#Ah -> As
        self._all_clause.append(prop_vs["rho"] == sys_vs["rho"])#Ah -> As
        #self._all_clause.append(motor_vs["I_motor"] * motor_vs["R_w"] == motor_vs["V_motor"] - motor_vs["omega_motor"] / motor_vs["K_v"])#Ah -> As
        self._vs_dict["system"] = sys_vs
        # set obj_lower_bound requirement
        if obj_lower_bound is not None:
            print("Set Lower bound: ", obj_lower_bound)
            self._all_clause.append(sys_vs["thrust_sum"] - sys_vs["weight_sum"] > obj_lower_bound)
        # 


        #self._all_clause.append(motor_vs["omega_motor"] > 2)#Ah -> As
        #self._all_clause.append(battery_vs["I_batt"] == 96)#Ah -> As
        # objective

    def solve(self, c_library: Library):
        solver = z3.Solver()
        solver.add(self._all_clause)
        ret = solver.check()
        #print(solver.assertions())
        if ret == z3.sat:# SAT
            print("SAT")
            model = solver.model()      
            #print(model)
            self.print_metric(model=model)
            propeller, motor, battery = self.get_component_selection(model=model, c_library=c_library)
            print("Found Component:")
            print(f"    Propeller: {propeller.id}")
            print(f"    Motor: {motor.id}")
            print(f"    Battery: {battery.id}") 
            thrust = model[self._vs_dict["system"]["thrust_sum"]].numerator_as_long()/model[self._vs_dict["system"]["thrust_sum"]].denominator_as_long()
            weight = model[self._vs_dict["system"]["weight_sum"]].numerator_as_long()/model[self._vs_dict["system"]["weight_sum"]].denominator_as_long()
            return thrust - weight
        else:
            print("UNSAT")
            return False

    def get_component_selection(self, model, c_library: Library):
        battery = None
        motor = None
        propeller = None
        for name, v in self._vs_dict["prop_select"].items():
            if z3.is_true(model[v]):
                propeller = c_library.components[name]
        for name, v in self._vs_dict["battery_select"].items():
            if z3.is_true(model[v]):
                battery = c_library.components[name]
        for name, v in self._vs_dict["motor_select"].items():
            if z3.is_true(model[v]):
                motor = c_library.components[name]    

        return propeller, motor, battery

    def print_metric(self, model):
        print("===================Component Selection Metric=====================")
        print("    Thrust: ", model[self._vs_dict["system"]["thrust_sum"]].numerator_as_long()/model[self._vs_dict["system"]["thrust_sum"]].denominator_as_long())    
        print("    Weight: ", model[self._vs_dict["system"]["weight_sum"]].numerator_as_long()/model[self._vs_dict["system"]["weight_sum"]].denominator_as_long())  
        print("    Omega_prop: ", model[self._vs_dict["propeller"]["omega_prop"]])
        print("    Omega_motor: ", model[self._vs_dict["motor"]["omega_motor"]])
        print("    Torque: ", model[self._vs_dict["motor"]["torque_motor"]].numerator_as_long()/model[self._vs_dict["motor"]["torque_motor"]].denominator_as_long())  
        print("    Torque: ", model[self._vs_dict["propeller"]["torque_prop"]].numerator_as_long()/model[self._vs_dict["motor"]["torque_motor"]].denominator_as_long())  
        print("    Current Battery: ", model[self._vs_dict["battery"]["I_batt"]].numerator_as_long()/model[self._vs_dict["battery"]["I_batt"]].denominator_as_long())  
        print("    Current Battery (Motor): ", model[self._vs_dict["motor"]["I_motor"]].numerator_as_long()/model[self._vs_dict["motor"]["I_motor"]].denominator_as_long())  
        print("    Voltage (Motor): ", model[self._vs_dict["motor"]["V_motor"]])
        print("    Capacity: ", model[self._vs_dict["battery"]["capacity"]].numerator_as_long()/model[self._vs_dict["battery"]["capacity"]].denominator_as_long())  
        print("    I_max: ", model[self._vs_dict["battery"]["I_max"]].numerator_as_long()/model[self._vs_dict["battery"]["I_max"]].denominator_as_long())  
        print("    V_battery: ", model[self._vs_dict["battery"]["V_battery"]].numerator_as_long()/model[self._vs_dict["battery"]["V_battery"]].denominator_as_long())  
        print("    C_t: ", model[self._vs_dict["propeller"]["C_t"]].numerator_as_long()/model[self._vs_dict["propeller"]["C_t"]].denominator_as_long())  
        print("    C_p: ", model[self._vs_dict["propeller"]["C_p"]].numerator_as_long()/model[self._vs_dict["propeller"]["C_p"]].denominator_as_long())  
        print("    K_t: ", model[self._vs_dict["motor"]["K_t"]].numerator_as_long()/model[self._vs_dict["motor"]["K_t"]].denominator_as_long())  
        print("    K_v: ", model[self._vs_dict["motor"]["K_v"]].numerator_as_long()/model[self._vs_dict["motor"]["K_v"]].denominator_as_long())  
        print("    R_w: ", model[self._vs_dict["motor"]["R_w"]].numerator_as_long()/model[self._vs_dict["motor"]["R_w"]].denominator_as_long())  
        print("    I_idle: ", model[self._vs_dict["motor"]["I_idle"]].numerator_as_long()/model[self._vs_dict["motor"]["I_idle"]].denominator_as_long())  
        print("    P_max_motor: ", model[self._vs_dict["motor"]["P_max_motor"]].numerator_as_long()/model[self._vs_dict["motor"]["P_max_motor"]].denominator_as_long())  
        print("    I_max_motor: ", model[self._vs_dict["motor"]["I_max_motor"]].numerator_as_long()/model[self._vs_dict["motor"]["I_max_motor"]].denominator_as_long())  
        print("    Diameter: ", model[self._vs_dict["propeller"]["diameter"]].numerator_as_long()/model[self._vs_dict["propeller"]["diameter"]].denominator_as_long())  
        print("==================================================================")
    def solve_optimize(self, c_library: Library, max_iter = 0):
        num_iter = 0
        propeller = None
        motor = None 
        battery = None
        solver = z3.Solver()
        #solver = z3.Optimize()
        solver.add(self._all_clause)
        ret = solver.check()
        while ret == z3.sat:
            model = solver.model()   
            self.print_metric(model=model)
            propeller, motor, battery = self.get_component_selection(model=model, c_library=c_library)
            print("Found Component:")
            print(f"    Propeller: {propeller.id}")
            print(f"    Motor: {motor.id}")
            print(f"    Battery: {battery.id}") 
            # count progress
            print(num_iter)
            if num_iter >= max_iter:
                break
            else: 
                num_iter += 1
            # set for next iteration
            thrust = model[self._vs_dict["system"]["thrust_sum"]].numerator_as_long()/model[self._vs_dict["system"]["thrust_sum"]].denominator_as_long()
            weight = model[self._vs_dict["system"]["weight_sum"]].numerator_as_long()/model[self._vs_dict["system"]["weight_sum"]].denominator_as_long()
            solver.add(self._vs_dict["system"]["thrust_sum"] - self._vs_dict["system"]["weight_sum"] >= thrust - weight + 1)
            ret = solver.check()
        if propeller is None or motor is None or battery is None:
            print("Fail.....")

        return propeller, motor, battery



class ContractTemplate():
    """Class of Contract Template, which handles information in the domain knowledge"""
    def __init__(self, constraints, behaviors):
        """associate theory: the background theory to reason about assume and guarantee"""
        self._constraints = constraints
        self._behaviors = behaviors

    def list_behavior(self):
        pass

    def instantiate(port_assignments) -> Contract:
        pass


class ContractLibrary():
    """Class ContractLibrary works as manager and process domain-knowledge input from designer to create
    design platform and perform optimization"""
    def __init__(self):
        self._contract_dict = {}

    def addContract(self, comp_type: CType, contract:Contract):
        self._contract_dict[comp_type] = contract


    def getContract(self, comp_type: CType):
        return self._contract_dict[comp_type]

