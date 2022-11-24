from sym_cps.contract.tester.uav_contract import UAVContract
from sym_cps.contract.tool.component_interface import ComponentInterface
from sym_cps.contract.tool.contract_instance import ContractInstance
from sym_cps.contract.tool.contract_system import ContractSystem
from sym_cps.contract.tool.contract_template import ContractTemplate
from sym_cps.contract.tool.solver.z3_interface import Z3Interface
from sym_cps.representation.design.concrete import DConcrete
from sym_cps.representation.library import Library, LibraryComponent
from sym_cps.representation.tools.parsers.parse import parse_library_and_seed_designs
from sym_cps.representation.tools.parsers.parsing_prop_table import parsing_prop_table


class SimplifiedSelector:
    def __init__(self):
        pass

    def set_library(self, library: Library):
        self._c_library = library
        self._table_dict = parsing_prop_table(library=self._c_library)

    def select_all(self, d_concrete: DConcrete, verbose: bool = True, body_weight: float = 0):
        num_batteries, num_propellers, num_motors, num_batt_controllers = self.count_components(d_concrete=d_concrete)
        self._uav_contract = UAVContract(table_dict=self._table_dict, num_motor=num_motors, num_battery=num_batteries)
        self._uav_contract.set_rpm(rpm=18000)
        self._uav_contract.set_speed(v=19)
        self._uav_contract.set_contract_simplified()
        contract_system = self.build_contract_system(verbose=verbose, component_list=None)
        # TODO make a selection
        sys_inst, sys_connection = self._set_check_max_voltage_system_contract(body_weight=body_weight)
        self.set_selection(contract_system=contract_system, sys_inst=sys_inst)
        ret = contract_system.select(
            sys_inst=sys_inst, sys_connection_map=sys_connection, max_iter=10, timeout_milliseconds=100000
        )
        contract_system.print_selection_result(ret=ret)
        # collect actual result
        battery = ret[contract_system.get_instance("Battery")]
        motor = ret[contract_system.get_instance("Motor")]
        propeller = ret[contract_system.get_instance("Propeller")]
        battery = self._c_library.components[battery["name"]]
        motor = self._c_library.components[motor["name"]]
        propeller = self._c_library.components[propeller["name"]]
        return battery, motor, propeller

    def check(self, d_concrete: DConcrete, verbose: bool = True, body_weight: float = 0):
        num_batteries, num_propellers, num_motors, num_batt_controllers = self.count_components(d_concrete=d_concrete)
        component_list = self.dconcrete_component_lists(d_concrete=d_concrete)
        self._uav_contract = UAVContract(table_dict=self._table_dict, num_motor=num_motors, num_battery=num_batteries)
        self._uav_contract.set_rpm(rpm=10000)
        self._uav_contract.set_speed(v=19)
        self._uav_contract.set_contract_simplified()
        contract_system = self.build_contract_system(verbose=verbose, component_list=component_list)

        sys_inst, sys_connection = self._set_check_system_contract(body_weight=body_weight)
        contract_system.find_behavior(sys_inst=sys_inst, sys_connection_map=sys_connection)

    def set_selection(self, contract_system: ContractSystem, sys_inst: ContractInstance):
        selection_list = ["Battery", "Propeller", "Motor"]
        for type_str in selection_list:
            selection_cand_library = list(self._c_library.components_in_type[type_str])

            # if type_str == "Battery":
            #    selection_cand_library = [self._c_library.components["TurnigyGraphene6000mAh6S75C"],
            #                              self._c_library.components["Tattu25C11000mAh6S1PHV"]
            #                             ]
            # if type_str == "Motor":
            #     selection_cand_library = [self._c_library.components["t_motor_AT4130KV300"],
            #                               self._c_library.components["t_motor_AT4130KV300"]]
            # if type_str == "Propeller":
            #     selection_cand_library = [self._c_library.components["apc_propellers_17x6"],
            #                                 self._c_library.components["apc_propellers_18x5_5MR"]]
            selection_cand_list = [
                self._uav_contract.hackathon_property_interface_fn_aggregated(cand) for cand in selection_cand_library
            ]
            # TODO insert debug code
            contract_system.set_selection(contract_system.get_instance(type_str), candidate_list=selection_cand_list)

        def obj_expr(vs):
            return [
                1 * (vs["thrust_sum"] - vs["weight_sum"]) + 20 * vs["batt_capacity"] * vs["V_battery"] / (vs["V_motor"] * vs["I_motor"])
            ]

        def obj_fn():
            thrust_sum = contract_system.get_metric_inst(inst=sys_inst, port_property_name="thrust_sum")
            weight_sum = contract_system.get_metric_inst(inst=sys_inst, port_property_name="weight_sum")
            capacity = contract_system.get_metric_inst(inst=sys_inst, port_property_name="batt_capacity")
            V_motor = contract_system.get_metric_inst(inst=sys_inst, port_property_name="V_motor")
            V_battery = contract_system.get_metric_inst(inst=sys_inst, port_property_name="V_battery")
            I_motor = contract_system.get_metric_inst(inst=sys_inst, port_property_name="I_motor")
            return 1 * (thrust_sum - weight_sum) + 20 * capacity * V_battery / V_motor / I_motor

        obj_val = 0
        contract_system.set_objective(expr=obj_expr, value=obj_val, evaluate_fn=obj_fn)

    def select_single_iterate(self, d_concrete: DConcrete, comp_type: str, verbose=True, body_weight=0):
        # for a battery, we want to check if the largest voltage is OK for the system
        num_batteries, num_propellers, num_motors, num_batt_controllers = self.count_components(d_concrete=d_concrete)
        component_list = self.dconcrete_component_lists(d_concrete=d_concrete)
        self._uav_contract = UAVContract(table_dict=self._table_dict, num_motor=num_motors, num_battery=num_batteries)
        self._uav_contract.set_contract_simplified()

        comps = []
        best_comp = None
        best_diff = 0  # float("inf")
        for comp in list(self._c_library.components_in_type[comp_type]):
            # for batt in [self._c_library.components["TurnigyGraphene1000mAh2S75C"]]:
            # for comp in [self._c_library.components["Tattu25C10000mAh4S1P"]]:
            self._uav_contract.set_rpm(rpm=18000)
            self._uav_contract.set_speed(v=19)
            component_list[comp_type]["lib"] = [comp] * len(component_list[comp_type]["lib"])
            contract_system = self.build_contract_system(verbose=verbose, component_list=component_list)
            sys_inst, sys_connection = self._set_check_max_voltage_system_contract(body_weight=body_weight)
            is_refine = contract_system.check_refinement(sys_inst=sys_inst, sys_connection_map=sys_connection)
            # is_refine = contract_system.find_behavior(sys_inst=sys_inst, sys_connection_map=sys_connection)
            # compute something....

            if is_refine:
                contract_system.set_solver(Z3Interface())
                contract_system.find_behavior(sys_inst=sys_inst, sys_connection_map=sys_connection)
                thrust = contract_system.get_metric_inst(inst=sys_inst, port_property_name="thrust_sum")
                weight = contract_system.get_metric_inst(inst=sys_inst, port_property_name="weight_sum")
                obj = thrust - weight
                comps.append((comp, obj))

        for comp, val in comps:
            print(comp.id, end="")
            self._uav_contract.set_rpm(rpm=10000)
            self._uav_contract.set_speed(v=19)
            component_list[comp_type]["lib"] = [comp] * len(component_list[comp_type]["lib"])
            contract_system = self.build_contract_system(verbose=verbose, component_list=component_list)
            sys_inst, sys_connection = self._set_check_balance_system_contract(body_weight=body_weight)
            is_find = contract_system.find_behavior(sys_inst=sys_inst, sys_connection_map=sys_connection)
            if is_find:
                V = contract_system.get_metric_inst(inst=sys_inst, port_property_name="V_motor")
                I = contract_system.get_metric(inst_name="Motor", port_property_name="I_motor")
                C = contract_system.get_metric(inst_name="Battery", port_property_name="capacity")
                v_batt = contract_system.get_metric(inst_name="Battery", port_property_name="V_battery")
                obj = 20 * C * v_batt / (V * I) + 1 * val
                # obj = C / (V * I)
                print(": ", obj, v_batt / V, end="")
                if obj > best_diff and v_batt * 0.95 >= V:
                    best_diff = obj
                    best_comp = comp
            print("")
        print("Best: ", best_comp.id, best_diff)
        return best_comp, best_diff

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
            ComponentInterface(name="I_motor", sort="real"),
            ComponentInterface(name="V_battery", sort="real"),
        ]
        system_property_name_list = []

        def system_assumption(vs):
            weight_sum = (vs["W_batt"] + body_weight + vs[f"W_prop"] + vs[f"W_motor"]) * 9.81
            return [
                vs["V_battery"] == vs["V_motor"],
                # vs["V_motor"] == 7.4,
                vs["rho"] == 1.225,
                vs["weight_sum"] == weight_sum,
            ]

        def system_guarantee(vs):

            ret_clauses = [vs["thrust_sum"] >= vs["weight_sum"]]

            return ret_clauses

        system_contract = ContractTemplate(
            name="System",
            port_list=system_port_name_list,
            property_list=system_property_name_list,
            guarantee=system_guarantee,
            assumption=system_assumption,
        )
        sys_connection_map = {
            "Propeller": [("thrust_sum", "thrust"), ("W_prop", "W_prop"), ("rho", "rho")],
            "Motor": [("W_motor", "W_motor"), ("V_motor", "V_motor"), ("I_motor", "I_motor")],
            "Battery": [
                ("W_batt", "W_batt"),
                ("batt_capacity", "capacity"),
                ("I_battery", "I_batt"),
                ("V_battery", "V_battery"),
            ],
        }
        system_instance = ContractInstance(template=system_contract, instance_name="System")
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
            ComponentInterface(name="V_battery", sort="real"),
        ]
        system_property_name_list = []

        def system_assumption(vs):
            weight_sum = (vs["W_batt"] + body_weight + vs[f"W_prop"] + vs[f"W_motor"]) * 9.81
            return [vs["thrust_sum"] == vs["weight_sum"], vs["rho"] == 1.225, vs["weight_sum"] == weight_sum]

        def system_guarantee(vs):

            ret_clauses = [vs["thrust_sum"] >= vs["weight_sum"], vs["I_battery"] <= vs["batt_capacity"] * 3600 / 200]

            return ret_clauses

        system_contract = ContractTemplate(
            name="System",
            port_list=system_port_name_list,
            property_list=system_property_name_list,
            guarantee=system_guarantee,
            assumption=system_assumption,
        )
        sys_connection_map = {
            "Propeller": [("thrust_sum", "thrust"), ("W_prop", "W_prop"), ("rho", "rho")],
            "Motor": [("W_motor", "W_motor"), ("V_motor", "V_motor"), ("I_motor", "I_motor")],
            "Battery": [
                ("W_batt", "W_batt"),
                ("batt_capacity", "capacity"),
                ("I_battery", "I_batt"),
                ("V_battery", "V_battery"),
            ],
        }
        system_instance = ContractInstance(template=system_contract, instance_name="System")
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
            ComponentInterface(name="thrust_sum", sort="real"),
        ]
        system_property_name_list = []

        def system_assumption(vs):
            weight_sum = (vs["W_batt"] + body_weight + vs[f"W_prop"] + vs[f"W_motor"]) * 9.81
            return [
                # vs["I_battery"] <= vs["batt_capacity"] * 3600 / 400,
                vs["rho"] == 1.225,
                vs["weight_sum"] == weight_sum,
            ]

        def system_guarantee(vs):

            ret_clauses = [vs["thrust_sum"] >= vs["weight_sum"]]

            return ret_clauses

        system_contract = ContractTemplate(
            name="System",
            port_list=system_port_name_list,
            property_list=system_property_name_list,
            guarantee=system_guarantee,
            assumption=system_assumption,
        )
        sys_connection_map = {
            "Propeller": [("thrust_sum", "thrust"), ("W_prop", "W_prop"), ("rho", "rho")],
            "Motor": [("W_motor", "W_motor")],
            "Battery": [("W_batt", "W_batt"), ("batt_capacity", "capacity"), ("I_battery", "I_batt")],
        }
        system_instance = ContractInstance(template=system_contract, instance_name="System")
        return system_instance, sys_connection_map

    def build_contract_system(self, verbose, component_list):
        contract_system = ContractSystem(verbose=verbose)
        contract_system.set_solver(Z3Interface())
        # Propeller
        contract_type_list = ["Propeller", "Motor", "Battery", "BatteryController"]
        contract_insts = {}
        for type_str in contract_type_list:
            properties = None
            if component_list is not None:
                properties = self._uav_contract.hackathon_property_interface_fn_aggregated(
                    component_list[type_str]["lib"][0]
                )
            contract_inst = ContractInstance(
                template=self._uav_contract.get_contract(type_str),
                instance_name=type_str,
                component_properties=properties,
            )
            contract_system.add_instance(contract_inst)

        # connect
        propeller_motor_connection = [
            ("torque_prop", "torque_motor"),
            ("omega_prop", "omega_motor"),
            ("shaft_motor", "shaft_motor"),
        ]
        motor_batt_contr_connection = [("I_motor", "I_motor"), ("V_motor", "V_motor")]
        batt_contr_connection = [("I_battery", "I_batt"), ("V_battery", "V_battery")]
        contract_system.compose(
            contract_system.get_instance("Propeller"), contract_system.get_instance("Motor"), propeller_motor_connection
        )
        contract_system.compose(
            contract_system.get_instance("Motor"),
            contract_system.get_instance("BatteryController"),
            motor_batt_contr_connection,
        )
        contract_system.compose(
            contract_system.get_instance("BatteryController"),
            contract_system.get_instance("Battery"),
            batt_contr_connection,
        )

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
        propeller: LibraryComponent = None,
        motor: LibraryComponent = None,
        battery: LibraryComponent = None,
    ):
        for component in design_concrete.components:
            if component.c_type.id == "Propeller":
                if propeller is not None:
                    component.library_component = propeller
            if component.c_type.id == "Battery":
                if battery is not None:
                    component.library_component = battery
            if component.c_type.id == "Motor":
                if motor is not None:
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

    def random_local_search(self, d_concrete: DConcrete):
        best_score = 0
        best_prop = None
        best_batt = None
        best_motor = None
        batteries = [self._c_library.components_in_type["Battery"]]
        propellers = [self._c_library.components_in_type["Propeller"]]
        motors = [self._c_library.components_in_type["Motor"]]
        for j in range(20):
            for i in range(3):
                battery, _ = self.select_single_iterate(
                    d_concrete=self._testquad_design, comp_type="Battery", body_weight=2.0, verbose=False
                )
                self.replace_with_component(design_concrete=self._testquad_design, battery=battery)
                # self.check(d_concrete=self._testquad_design, verbose=True, body_weight=1.0)
                propeller, _ = self.select_single_iterate(
                    d_concrete=self._testquad_design, comp_type="Propeller", body_weight=2.0, verbose=False
                )
                self.replace_with_component(design_concrete=self._testquad_design, propeller=propeller)
                motor, score = self.select_single_iterate(
                    d_concrete=self._testquad_design, comp_type="Motor", body_weight=2.0, verbose=False
                )
                self.replace_with_component(design_concrete=self._testquad_design, motor=motor)

                if score > best_score:
                    best_prop = propeller
                    best_motor = motor
                    best_batt = battery    
            # get random components



    def runTest(self):
        self._c_library, self._seed_designs = parse_library_and_seed_designs()
        self.set_library(library=self._c_library)

        self._testquad_design, _ = self._seed_designs["TestQuad_Cargo"]

        for comp in self._testquad_design.components:
            print(comp.id, comp.library_component.id)
        self._testquad_design.name += "_comp_opt"

        battery, motor, propeller = self.select_all(d_concrete=self._testquad_design, verbose=True, body_weight=2.0)

        self.replace_with_component(
            design_concrete=self._testquad_design, motor=motor, battery=battery, propeller=propeller
        )
        #self.check(d_concrete=self._testquad_design)
        for i in range(3):
            battery, _ = self.select_single_iterate(
                d_concrete=self._testquad_design, comp_type="Battery", body_weight=2.0, verbose=False
            )
            self.replace_with_component(design_concrete=self._testquad_design, battery=battery)
            # self.check(d_concrete=self._testquad_design, verbose=True, body_weight=1.0)
            propeller, _ = self.select_single_iterate(
                d_concrete=self._testquad_design, comp_type="Propeller", body_weight=2.0, verbose=False
            )
            self.replace_with_component(design_concrete=self._testquad_design, propeller=propeller)
            motor, _ = self.select_single_iterate(
                d_concrete=self._testquad_design, comp_type="Motor", body_weight=2.0, verbose=False
            )
            self.replace_with_component(design_concrete=self._testquad_design, motor=motor)
        from sym_cps.shared.objects import ExportType

        self._testquad_design.export(ExportType.JSON)
        from sym_cps.shared.paths import designs_folder

        self._testquad_design.evaluate(study_params=designs_folder / self._testquad_design.name / "study_params.csv")


if __name__ == "__main__":
    selector = SimplifiedSelector()
    selector.runTest()
