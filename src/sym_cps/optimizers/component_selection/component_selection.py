from sym_cps.representation.design.topology import DTopology
from sym_cps.representation.design.concrete import DConcrete
from sym_cps.representation.library import LibraryComponent
from sym_cps.representation.library import Library
from sym_cps.representation.tools.parsers.parsing_prop_table import parsing_prop_table
from sym_cps.contract.contract import Contract, ContractManager
from sym_cps.representation.library.elements.perf_table import PerfTable

import time
class ComponentSelectionContract():
    """Using Contracts, the input from designer knowledge, to facilitate selection of component
       and get a quick result without huge learning from scratch 
       This is a simplified version where all the contracts are hardcoded...
       Therefore, this strategy is domain specific.
    """
    def __init__(self, c_library: Library):
        self._library = c_library
        self._table_dict = parsing_prop_table(c_library)


    def select_hackathon(self, design_topology:DTopology, design_concrete: DConcrete = None, max_iter = 10):
        print(" ")
        #TODO use the d concrete as a lower bound to find a better one


        """Instantiate the contract"""
        """Get topology (simplified as just counting and hard-coded the number of each typed)"""
        manager = ContractManager()
        num_batteries, num_propellers, num_motors, num_batt_controllers = ComponentSelectionContract.count_components(d_topology=design_topology)
        """Use seed design as a lower bound"""
        obj = None
        if design_concrete is not None:
            obj = self.check_selection(design_concrete=design_concrete, design_topology=design_topology)
        """Create the contracts based on the topology"""
        manager.hackathon_contract(num_battery=num_batteries, num_motor=num_motors)
        """Form the contract-based optimization problem"""
        manager.hackathon_compose( num_battery=num_batteries, 
                                num_motor=num_motors, 
                                c_library=self._library, 
                                table_dict=self._table_dict, 
                                better_selection_encoding=True,
                                obj_lower_bound = obj)
        """Solver the OMT problem to optimize selection of components """
        start = time.time()
        propeller, motor, battery = manager.solve_optimize(c_library=self._library, max_iter=max_iter)
        end = time.time()
        print("Solving Time:", end - start)
        return propeller, motor, battery

    def replace_with_component(self, design_concrete: DConcrete, propeller:LibraryComponent, motor:LibraryComponent, battery: LibraryComponent):
        for component in design_concrete.components:
            if component.c_type.id == "Propeller":
                component.library_component = propeller
            if component.c_type.id == "Battery_UAV":
                component.library_component = battery
            if component.c_type.id == "Motor":
                component.library_component = motor


    def check_selection(self, design_topology:DTopology, 
                              design_concrete: DConcrete = None, 
                              motor: LibraryComponent = None,
                              propeller = None, 
                              battery = None):
        if motor is None or battery is None or battery is None:
            if design_concrete is not None:
                """get concrete component"""
                #battery_controller: LibraryComponent
                for component in design_concrete.components:
                    if component.c_type.id == "Propeller":
                        propeller = component.library_component
                    if component.c_type.id == "Battery_UAV":
                        battery = component.library_component
                    if component.c_type.id == "Motor":
                        motor = component.library_component
                    # if component.c_type.id == "BatteryController":
                    #     battery_controller = component.library_component
            else:
                print("Error, No component selection found for the type")
                return False
        
        print("Check Component:")
        print(f"Propeller: {propeller.id}")
        print(f"Motor: {motor.id}")
        print(f"Battery: {battery.id}")
        #print(f"BatteryController: {battery_controller.id}")
        """Get topology (simplified as just counting and hard-coded the number of each typed)"""
        num_batteries, num_propellers, num_motors, num_batt_controllers = ComponentSelectionContract.count_components(d_topology=design_topology)
        manager = ContractManager()
        """Create the contracts based on the topology"""
        manager.hackathon_contract(num_battery=num_batteries, num_motor=num_motors)
        """Form the contract-based componennt selection optimization problem"""
        start = time.time()
        objective = manager.check_selection(num_battery=num_batteries, 
                                num_motor=num_motors, 
                                c_library=self._library, 
                                table_dict=self._table_dict, 
                                battery=battery,
                                motor=motor,
                                propeller=propeller)
        """Solver the SMT problem to optimize selection of components """
        end = time.time()
        print("Solving Time:", end - start)   
        return objective

    @staticmethod
    def count_components(d_topology: DTopology):
        num_batteries = 0
        num_propellers = 0
        num_motors = 0
        num_batt_controllers = 0
        for node in d_topology.nodes:
            c_type = node["c_type"]
            if c_type.id == "Propeller":
                num_propellers += 1
            elif c_type.id == "Battery_UAV":
                num_batteries += 1
            elif c_type.id == "Motor":
                num_motors += 1
            elif c_type.id == "BatteryController":
                num_batt_controllers += 1
        return num_batteries, num_propellers, num_motors, num_batt_controllers


    def set_topology():
        return NotImplementedError


    def set_contract():
        """Accept Contract files"""
        return NotImplementedError



        
        Contracts["Propeller"] = Contract(motor_name_list, motor_assumtion, motor_guarantee)


    def select(self, d_topology: DTopology) -> dict[int, LibraryComponent]:
        """Select the motor propeller and battery"""

    def propeller_motor_g(i_motor, rho, speed, motor: LibraryComponent, propeller: LibraryComponent, 
                            table_dict:dict[LibraryComponent, PerfTable]) -> tuple[float, float, float]:
        """return the thrust and voltage of the motor given the input motor current
            Return: thrust, v_motor, weight, P_motor_max, I_motor_max
        """
        # ports get value
        R_w : float = motor.properties["INTERNAL_RESISTANCE"].value / 1000 # Ohm
        K_t : float = motor.properties["KT"].value
        K_v : float = motor.properties["KV"].value * (2 * math.pi)/60 # rpm/V to rad/(V-sec)
        I_idle : float = motor.properties["IO_IDLE_CURRENT_10V"].value
        diameter: float = propeller.properties["DIAMETER"].value / 1000
        shaft_diameter_motor: float = motor.properties["SHAFT_DIAMETER"].value
        shaft_diameter_propeller: float = propeller.properties["SHAFT_DIAMETER"].value
        #print(table.get_value(rpm = 13000, v = 90, label="Cp"))
        table = table_dict[propeller]
        C_p: float = table.get_value(rpm = 18000, v = speed, label="Cp")#0.0659 
        C_t: float = table.get_value(rpm = 18000, v = speed, label="Ct")#0.1319

        W_prop = propeller.properties["Weight"].value
        W_motor = motor.properties["WEIGHT"].value
        I_max = motor.properties["MAX_CURRENT"].value
        P_max = motor.properties["MAX_POWER"].value

        #check values
        print(f"R_w {R_w}, K_t {K_t}, K_v {K_v}, I_idle {I_idle}, diameter {diameter}",
            f"\nC_p {C_p}, C_t {C_t}, W_prop {W_prop}, W_motor {W_motor}, I_max {I_max}, P_max {P_max}")
        # contracts
        if i_motor - I_idle < 0 or C_p < 0:
            omega: float = 0
        else: 
            omega : float = math.sqrt((2*math.pi) ** 3 * K_t * (i_motor - I_idle) / (C_p * rho * diameter ** 5))
        thrust: float = (C_t * rho * omega ** 2 * diameter ** 4) / ((2*math.pi) ** 2)
        v_motor: float = i_motor * R_w + omega / K_v
        weight: float = W_prop + W_motor
        #print(f"omege {omega}, thrust {thrust}, v_mototr {v_motor}, i_motor {i_motor}, weight {weight}")
        return (thrust, v_motor, weight, I_max, P_max, shaft_diameter_motor, shaft_diameter_propeller)

    def battery_g(num_battery: int, battery: LibraryComponent) -> tuple[float, float, float]:
        """return capacity, i_battery
        """
        capacity: float = battery.properties["CAPACITY"].value * num_battery / 1000 # mAh -> Ah
        weight: float = battery.properties["WEIGHT"].value * num_battery
        voltage: float = battery.properties["VOLTAGE"].value
        I_max: float = (battery.properties["CONT_DISCHARGE_RATE"].value) * capacity# convert to mA
        
        return (capacity, weight, voltage, I_max)

    def battery_controller_g(i_battery, num_out: int, battery_controller):
        """convert the i_battery to the current for all motor"""
        return [i_battery/num_out * 0.95] * num_out

    def system_requirement_a(capacity: float) -> tuple[float, float, float]:
        """Requirement of the battery-motor-propeller system"""
            #  current (coming from the battery), speed, rho (air density  ! (kg/m^3))
            # Ah -> for 400s 
        #return (96, 0, 1.225)
        return (capacity * 3600 / 400, 0, 1.225 )

    def system_requirement_g(thrusts:list, vs_motor: list, v_battery, i_battery, weights: list, I_max, is_motor, 
                            Is_motor_max, Ps_motor_max, shaft_motor, shaft_prop):
        """Requirement of the battery-motor-propeller system"""
        # 0. motor and propeller should match
        if shaft_motor != shaft_prop:
            print("Unmatched motor/propeller")
            return False
        # 1. thrust > weight to ensure it can fly
        weight_sum = sum(weights)
        thrust_sum = sum(thrusts)
        if thrust_sum < weight_sum:
            print("Insufficient Thrust")
            print(f"thrust: {thrust_sum}, weight: {weight_sum}")
            return False
        # 2. the voltage should be allowed by the battery
        if any(v_motor > v_battery for v_motor in vs_motor):
            print("Unreachable voltage")
            print(vs_motor, v_battery)
            return False
        # 3. the current should be less than i_max
        if i_battery > I_max:
            print("battery current exceeds")
            print(i_battery, I_max)
            return False
        # 4. the motor power should be less than maximum
        if any(v_motor * i_motor > P_motor_max for (v_motor, i_motor, P_motor_max) in zip(vs_motor, is_motor, Ps_motor_max)):
            print("Motor Power Exceeds")
            print(Ps_motor_max, is_motor, vs_motor)
            return False
        if any(i_motor > I_motor_max for (i_motor, I_motor_max) in zip(is_motor, Is_motor_max)):
            print("Motor Current Exceeds")
            print(Is_motor_max, is_motor)
            return False
        return True

    def objective(thrusts:list, vs_motor: list, v_battery, i_battery, weights: list, I_max, is_motor, Is_motor_max, Ps_motor_max):
        weight_sum = sum(weights)
        thrust_sum = sum(thrusts)

        weight_margin = thrust_sum - weight_sum
        print(f"weight: {weight_sum}, thrust: {thrust_sum}")
        return weight_margin

    





