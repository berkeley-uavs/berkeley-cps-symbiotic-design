import time

from sym_cps.contract.contract import ContractManagerBruteForce

# from sym_cps.contract.contract_general import ContractGeneralManager
from sym_cps.contract.contract_composition import Hackathon2Contract
from sym_cps.representation.design.concrete import DConcrete
from sym_cps.representation.library import Library, LibraryComponent
from sym_cps.representation.tools.parsers.parsing_prop_table import parsing_prop_table


class ComponentSelectionContract:
    """Using Contracts, the input from designer knowledge, to facilitate selection of component
    and get a quick result without huge learning from scratch
    This is a simplified version where all the contracts are hardcoded...
    Therefore, this strategy is domain specific.
    """

    def __init__(self, c_library: Library):
        self._library = c_library
        self._table_dict = parsing_prop_table(c_library)

    def select_general(self, design_concrete: DConcrete, max_iter=10, timeout_millisecond=100000):

        manager = Hackathon2Contract(table_dict=self._table_dict, c_library=self._library)
        """Get topology (simplified as just counting and hard-coded the number of each typed)"""
        num_batteries, num_propellers, num_motors, num_batt_controllers = ComponentSelectionContract.count_components(
            d_concrete=design_concrete
        )
        """Instantiate the contract"""
        obj = None
        if design_concrete is not None:
            print("Calculate the initial objective function")
            component_dict_input = self.create_component_lists(d_concrete=design_concrete)
            obj = self.check_selection_general(design_concrete=design_concrete)
            print("Objective: ", obj)
        else:
            print("Currently not supported")
            return None
        """Create the contracts based on the topology"""
        manager.compose(
            num_battery=num_batteries,
            num_motor=num_motors,
            motor_ratio=[1] * num_motors,
            body_weight=0,
            better_selection_encoding=True,
            obj_lower_bound=obj,
        )
        """Solver the OMT problem to optimize selection of components """
        start = time.time()
        component_dict_ret = manager.optimize(max_iter=max_iter, timeout_millisecond=timeout_millisecond)
        end = time.time()
        print("Solving Time:", end - start)
        if component_dict_ret is None:
            print("No valid components found within time limit...")
            return None
        component_dict = self.match_result(component_dict_ret, component_dict_input)
        self.print_components(component_dict=component_dict)
        return component_dict

    def check_selection_general(self, design_concrete: DConcrete, component_dict: dict = None):
        if component_dict is None:
            if design_concrete is not None:
                """get concrete component"""
                component_dict = self.create_component_lists(d_concrete=design_concrete)
            else:
                print("Error, No component selection found for the type")
                return False
        print("Check Component:")
        self.print_components(component_dict=component_dict)
        num_batteries, num_propellers, num_motors, num_batt_controllers = ComponentSelectionContract.count_components(
            d_concrete=design_concrete
        )
        manager = Hackathon2Contract(table_dict=self._table_dict, c_library=self._library)
        start = time.time()
        objective = manager.check_selection(
            num_battery=num_batteries,
            num_motor=num_motors,
            battery=component_dict["Battery"]["lib"][0],
            motors=component_dict["Motor"]["lib"],
            propellers=component_dict["Propeller"]["lib"],
            body_weight=0,
            motor_ratio=[1.0] * num_motors,
        )
        end = time.time()
        print("Solving Time:", end - start)
        return objective

    def match_result(self, component_dict_ret, component_dict_input):
        for c_type_id, info in component_dict_ret.items():
            libs = info["lib"]
            if c_type_id == "Battery":
                component_dict_input[c_type_id]["lib"] = libs * len(component_dict_input[c_type_id]["comp"])
            else:
                component_dict_input[c_type_id]["lib"] = libs
        return component_dict_input

    def replace_with_component_general(self, component_dict: dict):
        for c_type_id, info in component_dict:
            comps = info["comp"]
            libs = info["lib"]
            for comp, lib in zip(comps, libs):
                comp.library_component = lib

    def select_hackathon(self, design_concrete: DConcrete, max_iter = 10, timeout_millisecond = 100000, body_weight = 0):
        print(" ")

        """Instantiate the contract"""
        """Get topology (simplified as just counting and hard-coded the number of each typed)"""
        manager = ContractManagerBruteForce()
        num_batteries, num_propellers, num_motors, num_batt_controllers = ComponentSelectionContract.count_components(
            d_concrete=design_concrete
        )
        """Use seed design as a lower bound"""
        obj = None
        if design_concrete is not None:
            obj = self.check_selection(design_concrete=design_concrete)
        """Create the contracts based on the topology"""
        manager.hackathon_contract(num_battery=num_batteries, num_motor=num_motors)
        """Form the contract-based optimization problem"""
        manager.hackathon_compose(
            num_battery=num_batteries,
            num_motor=num_motors,
            c_library=self._library,
            table_dict=self._table_dict,
            better_selection_encoding=True,
            body_weight=body_weight,
            obj_lower_bound=obj,
        )
        """Solver the OMT problem to optimize selection of components """
        start = time.time()
        propeller, motor, battery = manager.solve_optimize(
            c_library=self._library, max_iter=max_iter, timeout_millisecond=timeout_millisecond
        )
        end = time.time()
        print("Solving Time:", end - start)
        return propeller, motor, battery

    def replace_with_component(
        self,
        design_concrete: DConcrete,
        propeller: LibraryComponent,
        motor: LibraryComponent,
        battery: LibraryComponent,
    ):
        for component in design_concrete.components:
            if component.c_type.id == "Propeller":
                component.library_component = propeller
            if component.c_type.id == "Battery":
                component.library_component = battery
            if component.c_type.id == "Motor":
                component.library_component = motor

    def check_selection(self, design_concrete: DConcrete, motor: LibraryComponent = None, propeller=None, battery=None):
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
        num_batteries, num_propellers, num_motors, num_batt_controllers = ComponentSelectionContract.count_components(
            d_concrete=design_concrete
        )
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
    def count_components(d_concrete: DConcrete):
        num_batteries = 0
        num_propellers = 0
        num_motors = 0
        num_batt_controllers = 0
        for component in d_concrete.components:
            c_type = component.c_type
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
        component_dict = {}
        for component in d_concrete.components:
            c_type = component.c_type
            if c_type.id not in component_dict:
                component_dict[c_type.id] = {}
                component_dict[c_type.id]["comp"] = []
                component_dict[c_type.id]["lib"] = []

            component_dict[c_type.id]["comp"].append(component.library_component)
            component_dict[c_type.id]["lib"].append(component.library_component)

        return component_dict

    @staticmethod
    def print_components(component_dict: dict):
        print("============= Components Mapping ==============")
        for c_type_id, comp_info in component_dict.items():
            for n, comp in enumerate(comp_info["lib"]):
                print(f"    {c_type_id} {n}: {comp.id}")
        print("===============================================")
