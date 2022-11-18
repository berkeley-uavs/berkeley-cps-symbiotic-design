from sym_cps.representation.design.concrete import DConcrete
from sym_cps.representation.library import Library, LibraryComponent
from sym_cps.representation.tools.parsers.parsing_prop_table import parsing_prop_table
from sym_cps.representation.tools.parsers.parse import parse_library_and_seed_designs
from sym_cps.contract.tester.uav_contract import UAVContract
from sym_cps.contract.tool.contract_instance import ContractInstance
from sym_cps.contract.tool.contract_system import ContractSystem
from sym_cps.contract.tool.component_interface import ComponentInterface
from sym_cps.contract.tool.contract_template import ContractTemplate
from sym_cps.contract.tool.solver.z3_interface import Z3Interface
class SimplifiedSelector():
    def __init__(self):
        pass

    def set_library(self, library: Library):
        self._c_library = library
        self._table_dict = parsing_prop_table(library = self._c_library)

    def select_all(self, d_concrete: DConcrete, verbose = True, body_weight = 0):
        num_batteries, num_propellers, num_motors, num_batt_controllers = self.count_components()
        self._uav_contract = UAVContract(table_dict=self._table_dict, num_motor=num_motors, num_battery=num_batteries)
        self._uav_contract.set_contract_simplified()
        contract_system = self.build_contract_system(
            verbose=verbose,
            component_list=None
        )        

    def check(self, d_concrete: DConcrete, verbose = True, body_weight = 0):
        num_batteries, num_propellers, num_motors, num_batt_controllers = self.count_components(d_concrete=d_concrete)
        component_list = self.dconcrete_component_lists(d_concrete=d_concrete)
        self._uav_contract = UAVContract(table_dict=self._table_dict, num_motor=num_motors, num_battery=num_batteries)
        self._uav_contract.set_contract_simplified()
        contract_system = self.build_contract_system(
            verbose=verbose,
            component_list=component_list
        )
        
        sys_inst, sys_connection = self._set_check_system_contract(body_weight=body_weight)
        contract_system.find_behavior(sys_inst=sys_inst, sys_connection_map=sys_connection)
    
    def select_single_iterate(self, d_concrete: DConcrete, comp_type: str, verbose = True, body_weight = 0):
        # for a battery, we want to check if the largest voltage is OK for the system
        num_batteries, num_propellers, num_motors, num_batt_controllers = self.count_components(d_concrete=d_concrete)
        component_list = self.dconcrete_component_lists(d_concrete=d_concrete)
        self._uav_contract = UAVContract(table_dict=self._table_dict, num_motor=num_motors, num_battery=num_batteries)
        self._uav_contract.set_contract_simplified()
        
        comps = []
        best_comp = None
        best_diff = float("inf")
        for comp in self._c_library.components_in_type[comp_type]:
        #for batt in [self._c_library.components["TurnigyGraphene1000mAh2S75C"]]:
        #for batt in [self._c_library.components["TurnigyGraphene1000mAh4S75C"]]:
        
            component_list[comp_type]["lib"] = [comp] * len(component_list[comp_type]["lib"])
            contract_system = self.build_contract_system(
                verbose=verbose,
                component_list=component_list
            )
            sys_inst, sys_connection = self._set_check_max_voltage_system_contract(body_weight=body_weight)
            is_find = contract_system.find_behavior(sys_inst=sys_inst, sys_connection_map=sys_connection)
            # compute something....
            if is_find:
                comps.append(comp)

        for comp in comps:
            component_list[comp_type]["lib"] = [comp] * len(component_list[comp_type]["lib"])
            contract_system = self.build_contract_system(
                verbose=verbose,
                component_list=component_list
            )            
            sys_inst, sys_connection = self._set_check_balance_system_contract(body_weight=body_weight)
            is_find = contract_system.find_behavior(sys_inst=sys_inst, sys_connection_map=sys_connection)
            V = contract_system.get_metric_inst(inst=sys_inst, port_property_name="V_motor")
            I = contract_system.get_metric(inst_name="Motor", port_property_name="I_motor")
            obj = V * I
            if obj < best_diff:
                best_diff = obj
                best_comp = comp
        print(best_comp.id, best_diff)
        return best_comp

    def _set_check_max_voltage_system_contract(self, body_weight: float):
        system_port_name_list = [
            ComponentInterface(name="rho", sort="real"), 
            ComponentInterface(name="weight_sum", sort="real"), 
            ComponentInterface(name="I_battery", sort="real"), 
            ComponentInterface(name="batt_capacity", sort="real"),
            ComponentInterface(name="W_motor", sort="real"),
            ComponentInterface(name="W_prop", sort="real"),
            ComponentInterface(name="W_batt", sort="real"),
            ComponentInterface(name="thrust_sum", sort="real"),
            ComponentInterface(name="V_motor", sort="real"),
            ComponentInterface(name="V_battery", sort="real")
        ]
        system_property_name_list = []

        def system_assumption(vs):
            weight_sum = (
                vs["W_batt"]
                + body_weight
                + vs[f"W_prop"]
                + vs[f"W_motor"]
            ) * 9.81
            return [
                vs["V_battery"] == vs["V_motor"], 
                #vs["V_motor"] == 7.4, 
                vs["rho"] == 1.225,
                vs["weight_sum"] == weight_sum
            ]

        def system_guarantee(vs):

            ret_clauses = [
                vs["thrust_sum"] >= vs["weight_sum"]
            ]

            return ret_clauses

        system_contract = ContractTemplate(
            name="System",
            port_list=system_port_name_list,
            property_list=system_property_name_list,
            guarantee=system_guarantee,
            assumption=system_assumption,
        )
        sys_connection_map = {
            "Propeller": [
                ("thrust_sum", "thrust"),
                ("W_prop", "W_prop"),
                ("rho", "rho")
            ],
            "Motor": [
                ("W_motor", "W_motor"),
                ("V_motor", "V_motor")
            ],
            "Battery": [
                ("W_batt", "W_batt"),
                ("batt_capacity", "capacity"),
                ("I_battery", "I_batt"),
                ("V_battery", "V_battery")
            ]
        }
        system_instance = ContractInstance(
            template=system_contract,
            instance_name="System"
        )
        return system_instance, sys_connection_map 

    def _set_check_balance_system_contract(self, body_weight: float):
        system_port_name_list = [
            ComponentInterface(name="rho", sort="real"), 
            ComponentInterface(name="weight_sum", sort="real"), 
            ComponentInterface(name="I_battery", sort="real"), 
            ComponentInterface(name="batt_capacity", sort="real"),
            ComponentInterface(name="W_motor", sort="real"),
            ComponentInterface(name="W_prop", sort="real"),
            ComponentInterface(name="W_batt", sort="real"),
            ComponentInterface(name="thrust_sum", sort="real"),
            ComponentInterface(name="V_motor", sort="real"),
            ComponentInterface(name="I_motor", sort="real"),
            ComponentInterface(name="V_battery", sort="real")
        ]
        system_property_name_list = []

        def system_assumption(vs):
            weight_sum = (
                vs["W_batt"]
                + body_weight
                + vs[f"W_prop"]
                + vs[f"W_motor"]
            ) * 9.81
            return [
                vs["thrust_sum"] == vs["weight_sum"], 
                vs["rho"] == 1.225,
                vs["weight_sum"] == weight_sum
            ]

        def system_guarantee(vs):

            ret_clauses = [
                vs["thrust_sum"] >= vs["weight_sum"]
            ]

            return ret_clauses

        system_contract = ContractTemplate(
            name="System",
            port_list=system_port_name_list,
            property_list=system_property_name_list,
            guarantee=system_guarantee,
            assumption=system_assumption,
        )
        sys_connection_map = {
            "Propeller": [
                ("thrust_sum", "thrust"),
                ("W_prop", "W_prop"),
                ("rho", "rho")
            ],
            "Motor": [
                ("W_motor", "W_motor"),
                ("V_motor", "V_motor"),
                ("I_motor", "I_motor")
            ],
            "Battery": [
                ("W_batt", "W_batt"),
                ("batt_capacity", "capacity"),
                ("I_battery", "I_batt"),
                ("V_battery", "V_battery")
            ]
        }
        system_instance = ContractInstance(
            template=system_contract,
            instance_name="System"
        )
        return system_instance, sys_connection_map 

    def _set_check_system_contract(self, body_weight: float):
        system_port_name_list = [
            ComponentInterface(name="rho", sort="real"), 
            ComponentInterface(name="weight_sum", sort="real"), 
            ComponentInterface(name="I_battery", sort="real"), 
            ComponentInterface(name="batt_capacity", sort="real"),
            ComponentInterface(name="W_motor", sort="real"),
            ComponentInterface(name="W_prop", sort="real"),
            ComponentInterface(name="W_batt", sort="real"),
            ComponentInterface(name="thrust_sum", sort="real")
        ]
        system_property_name_list = []

        def system_assumption(vs):
            weight_sum = (
                vs["W_batt"]
                + body_weight
                + vs[f"W_prop"]
                + vs[f"W_motor"]
            ) * 9.81
            return [
                vs["I_battery"] == vs["batt_capacity"] * 3600 / 400, 
                vs["rho"] == 1.225,
                vs["weight_sum"] == weight_sum
            ]

        def system_guarantee(vs):

            ret_clauses = [
                vs["thrust_sum"] >= vs["weight_sum"]
            ]

            return ret_clauses

        system_contract = ContractTemplate(
            name="System",
            port_list=system_port_name_list,
            property_list=system_property_name_list,
            guarantee=system_guarantee,
            assumption=system_assumption,
        )
        sys_connection_map = {
            "Propeller": [
                ("thrust_sum", "thrust"),
                ("W_prop", "W_prop"),
                ("rho", "rho")
            ],
            "Motor": [
                ("W_motor", "W_motor")
            ],
            "Battery": [
                ("W_batt", "W_batt"),
                ("batt_capacity", "capacity"),
                ("I_battery", "I_batt")
            ]
        }
        system_instance = ContractInstance(
            template=system_contract,
            instance_name="System"
        )
        return system_instance, sys_connection_map

    def build_contract_system(self, verbose, component_list):

        contract_system = ContractSystem(verbose=verbose)
        contract_system.set_solver(Z3Interface())
        #Propeller
        contract_prop = ContractInstance(
            template=self._uav_contract.get_contract("Propeller"),
            instance_name="Propeller",
            component_properties=self._uav_contract.hackathon_property_interface_fn_aggregated(component_list["Propeller"]["lib"][0])
            )
        #Motor
        contract_motor = ContractInstance(
            template=self._uav_contract.get_contract("Motor"),
            instance_name="Motor",
            component_properties=self._uav_contract.hackathon_property_interface_fn_aggregated(component_list["Motor"]["lib"][0])
            )
        #Battery
        contract_batt = ContractInstance(
            template=self._uav_contract.get_contract("Battery"),
            instance_name="Battery",
            component_properties=self._uav_contract.hackathon_property_interface_fn_aggregated(component_list["Battery"]["lib"][0])
            )
        # Controller
        contract_controller = ContractInstance(
            template=self._uav_contract.get_contract("BatteryController"),
            instance_name="BatteryController",
            component_properties=self._uav_contract.hackathon_property_interface_fn_aggregated(component_list["BatteryController"]["lib"][0])
            )

        contract_system.add_instance(contract_prop)
        contract_system.add_instance(contract_motor)
        contract_system.add_instance(contract_batt)
        contract_system.add_instance(contract_controller)
        # connect
        propeller_motor_connection = [
            ("torque_prop", "torque_motor"),
            ("omega_prop", "omega_motor"),
            ("shaft_motor", "shaft_motor"),
        ]
        motor_batt_contr_connection = [("I_motor", "I_motor"), ("V_motor", "V_motor")]
        batt_contr_connection = [("I_battery", "I_batt"), ("V_battery", "V_battery")]
        contract_system.compose(contract_prop, contract_motor, propeller_motor_connection)
        contract_system.compose(contract_motor, contract_controller, motor_batt_contr_connection)
        contract_system.compose(contract_controller, contract_batt, batt_contr_connection)

        return contract_system


    def create_component_dict_list(self, components: list[LibraryComponent]):
        ret = [self._uav_contract.hackathon_property_interface_fn_aggregated(component=comp) for comp in components]

    def _create_component_dict_list_bpm(self):
        comp_batt = ret

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
    def replace_with_component(
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

    @staticmethod
    def dconcrete_component_lists(d_concrete: DConcrete):
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

    def runTest(self):
        self._c_library, self._seed_designs = parse_library_and_seed_designs()
        self.set_library(library=self._c_library)

        self._testquad_design, _ = self._seed_designs["TestQuad"]
        #self.check(d_concrete=self._testquad_design)
        self.select_single_iterate(d_concrete=self._testquad_design, comp_type="Propeller", body_weight=1.0)




if __name__ == "__main__":
    selector = SimplifiedSelector()
    selector.runTest()