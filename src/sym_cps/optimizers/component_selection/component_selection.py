from sym_cps.representation.design.topology import DTopology
from sym_cps.representation.design.concrete import DConcrete
from sym_cps.representation.library import LibraryComponent
from sym_cps.representation.library import Library
from sym_cps.representation.tools.parsers.parsing_prop_table import parsing_prop_table
from sym_cps.contract.contract import Contract, ContractManagerBruteForce
# from sym_cps.contract.contract_general import ContractGeneralManager
from sym_cps.representation.library.elements.perf_table import PerfTable
from sym_cps.contract.contract_composition import Hackathon2Contract



class ComponentSelectionContract:
    """Using Contracts, the input from designer knowledge, to facilitate selection of component
    and get a quick result without huge learning from scratch
    This is a simplified version where all the contracts are hardcoded...
    Therefore, this strategy is domain specific.
    """

    def __init__(self, c_library: Library):
        self._library = c_library
        self._table_dict = parsing_prop_table(c_library)


    def select_general(self, design_topology:DTopology, design_concrete: DConcrete = None, max_iter = 10, timeout_millisecond = 100000):
        
        
        manager = Hackathon2Contract(table_dict=self._table_dict, c_library=self._library)
        """Get topology (simplified as just counting and hard-coded the number of each typed)"""
        num_batteries, num_propellers, num_motors, num_batt_controllers = ComponentSelectionContract.count_components(d_topology=design_topology)
        """Instantiate the contract"""
        obj = None
        if design_concrete is not None:
            batteries, propellers, motors, batt_controllers =  self.create_component_lists(d_concrete=design_concrete)
            obj = self.check_selection(design_concrete=design_concrete, design_topology=design_topology)
        """Create the contracts based on the topology"""
        manager.compose(num_battery=num_batteries,
                        num_motor=num_motors,
                        motors=[[motor] for motor in motors],
                        propellers=[[prop] for prop in propellers],
                        batteries=[battery],
                        motor_ratio=[1]* num_motors,
                        body_weight=0,
                        better_selection_encoding=True,
                        obj_lower_bound=obj
                        )
        """Solver the OMT problem to optimize selection of components """
        start = time.time()
        propellers, motors, battery = manager.optimize(max_iter=max_iter, timeout_millisecond=timeout_millisecond)
        end = time.time()
        print("Solving Time:", end - start)
        return propellers, motors, battery

    def check_selection_general(self, 
                                design_concrete: DConcrete, 
                                design_topology: DTopology,
                                motors: list[LibraryComponent] = None,
                                propellers: list[LibraryComponent] = None, 
                                battery: LibraryComponent = None
                              ):
        if motors is None or battery is None or propellers is None:
            if design_concrete is not None:
                """get concrete component"""
                batteries, propellers, motors, _ =  self.create_component_lists(d_concrete=design_concrete)
                battery = batteries[0]
            else:
                print("Error, No component selection found for the type")
                return False
        print("Check Component:")
        self.print_components(propellers=propellers, motors=motors, batteries=[battery])
        num_batteries, num_propellers, num_motors, num_batt_controllers = ComponentSelectionContract.count_components(d_topology=design_topology)
        manager = Hackathon2Contract(table_dict=self._table_dict, c_library=self._library)
        start = time.time()
        objective = manager.check_selection(num_battery=num_batteries,
                                num_motor=num_motors,
                                battery=battery,
                                motors=motors,
                                propellers=propellers,
                                body_weight=0,
                                motor_ratio=[1.0]*num_motors)
        end = time.time()
        print("Solving Time:", end - start)   
        return objective        

        

    def select_hackathon(self, design_topology:DTopology, design_concrete: DConcrete = None, max_iter = 10, timeout_millisecond = 100000):
        print(" ")


        """Instantiate the contract"""
        """Get topology (simplified as just counting and hard-coded the number of each typed)"""
        manager = ContractManagerBruteForce()
        num_batteries, num_propellers, num_motors, num_batt_controllers = ComponentSelectionContract.count_components(d_topology=design_topology)
        """Use seed design as a lower bound"""
        obj = None
        if design_concrete is not None:
            obj = self.check_selection(design_concrete=design_concrete, design_topology=design_topology)
        """Create the contracts based on the topology"""
        manager.hackathon_contract(num_battery=num_batteries, num_motor=num_motors)
        """Form the contract-based optimization problem"""
        manager.hackathon_compose(
            num_battery=num_batteries,
            num_motor=num_motors,
            c_library=self._library,
            table_dict=self._table_dict,
            better_selection_encoding=True,
            obj_lower_bound=obj,
        )
        """Solver the OMT problem to optimize selection of components """
        start = time.time()
        propeller, motor, battery = manager.solve_optimize(c_library=self._library, max_iter=max_iter, timeout_millisecond = timeout_millisecond)
        end = time.time()
        print("Solving Time:", end - start)
        return propeller, motor, battery


    def replace_with_component(self, design_concrete: DConcrete, propeller:LibraryComponent, motor:LibraryComponent, battery: LibraryComponent):
        for component in design_concrete.components:
            if component.c_type.id == "Propeller":
                component.library_component = propeller
            if component.c_type.id == "Battery":
                component.library_component = battery
            if component.c_type.id == "Motor":
                component.library_component = motor


    def check_selection(self, design_topology:DTopology, 
                              design_concrete: DConcrete = None, 
                              motor: LibraryComponent = None,
                              propeller = None, 
                              battery = None):
        if motor is None or battery is None or propeller is None:
            if design_concrete is not None:
                """get concrete component"""
                # battery_controller: LibraryComponent
                for component in design_concrete.components:
                    if component.c_type.id == "Propeller":
                        propeller = component.library_component
                    if component.c_type.id == "Battery":
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
        # print(f"BatteryController: {battery_controller.id}")
        """Get topology (simplified as just counting and hard-coded the number of each typed)"""
        num_batteries, num_propellers, num_motors, num_batt_controllers = ComponentSelectionContract.count_components(d_topology=design_topology)
        manager = ContractManagerBruteForce()
        """Create the contracts based on the topology"""
        manager.hackathon_contract(num_battery=num_batteries, num_motor=num_motors)
        """Form the contract-based componennt selection optimization problem"""
        start = time.time()
        objective = manager.check_selection(
            num_battery=num_batteries,
            num_motor=num_motors,
            c_library=self._library,
            table_dict=self._table_dict,
            battery=battery,
            motor=motor,
            propeller=propeller,
        )
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
            elif c_type.id == "Battery":
                num_batteries += 1
            elif c_type.id == "Motor":
                num_motors += 1
            elif c_type.id == "BatteryController":
                num_batt_controllers += 1
        return num_batteries, num_propellers, num_motors, num_batt_controllers

    @staticmethod
    def create_component_lists(d_concrete: DConcrete):
        batteries = []
        propellers = []
        motors = []
        batt_controllers = []
        for component in d_concrete.components:
            c_type = component.c_type
            if c_type.id == "Propeller":
                propellers.append(component.library_component)
            elif c_type.id == "Battery":
                batteries.append(component.library_component)
            elif c_type.id == "Motor":
                motors.append(component.library_component)
            elif c_type.id == "BatteryController":
                batt_controllers.append(component.library_component)
        return batteries, propellers, motors, batt_controllers

    @staticmethod
    def print_components(propellers: list[LibraryComponent], motors: list[LibraryComponent], batteries: LibraryComponent):
        for n, prop in enumerate(propellers):
            print(f"Propeller {n}: {prop.id}")
        for n, motor in enumerate(motors):
            print(f"Motor {n}: {motor.id}")
        for n, battery in enumerate(batteries):
            print(f"Battery {n}: {battery.id}")


