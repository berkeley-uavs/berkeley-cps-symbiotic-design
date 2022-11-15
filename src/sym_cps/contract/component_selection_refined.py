import json
from sym_cps.shared.paths import data_folder
from sym_cps.contract.uav_contracts import UAVContract
from sym_cps.contract.tool.contract_tool import ContractManager, ContractTemplate
from sym_cps.representation.design.concrete import DConcrete
from sym_cps.contract.component_selection import Hackathon2Contract
from sym_cps.representation.tools.parsers.parsing_prop_table import parsing_prop_table
class RefineComponentSelection():
    def __init__(self, analysis_file, library):
        analysis_file = data_folder/ "ComponentLibrary" /"component_selection_analysis" / "motor_propeller_pair.json"
        self._analysis_file = analysis_file
        self._c_library = library
        self._table_dict = parsing_prop_table(library)


    def search(self, d_concrete: DConcrete):
        num_batteries, num_propellers, num_motors, num_batt_controllers = self.count_components(d_concrete=d_concrete)
        self._uav_contract: UAVContract = UAVContract(num_battery=num_batteries, num_motor=num_motors)
        self._contract = self._uav_contract.set_contract()
        motor_propeller_pairs = None
        with open(self._analysis_file, "r") as motor_propeller_pair_file:
            motor_propeller_pairs = json.load(motor_propeller_pair_file)
        # iterate all batteries

        ret_pair = []
        manager = Hackathon2Contract(table_dict=self._table_dict, c_library=self._c_library)
        for nb, batt in enumerate(list(self._c_library.components_in_type["Battery"])):
            for np, prop in enumerate(motor_propeller_pairs):
                print(nb," " ,np)
                batt_prop = self._uav_contract.hackthon_get_battery_property(batt,num_battery=num_batteries)
                prop_name = prop[0]
                motor_name = prop[1]
                max_v = prop[2]["max_v"]
                fly_i = prop[2]["min_fly"]["I"]
                fly_v = prop[2]["min_fly"]["V"]
                v_battery = batt_prop["V_battery"]
                capacity = batt_prop["capacity"]
                i_max = batt_prop["I_max"]

                if max_v < v_battery:
                    continue
                if v_battery < fly_v:
                    continue
                if capacity * 3600/400 < fly_i:
                    continue
                ret_pair.append([batt.id, prop_name, motor_name])

                objective = manager.check_selection(
                    num_battery=num_batteries,
                    num_motor=num_motors,
                    battery=batt,
                    motors=[self._c_library.components[motor_name]] * num_motors,
                    propellers=[self._c_library.components[prop_name]]* num_motors,
                    body_weight=0,
                    motor_ratio=[1.0] * num_motors,
                )
        print("complete")
        ret_file = data_folder /"ComponentLibrary" / "component_selection_analysis" / "full_result.json"
        with open(ret_file, "w") as outfile:
            json.dump(ret_pair, outfile, indent = 4)

                
                

    def get_system_contract():
        # target: find the number of propeller that can support the required thrust -> pick every propeller from motor-propeller which can generate required thrust. 
        # The correspsonding current is the key -> should not overflow the capacity
        # Not violating the max voltage -> check the battery voltage lower than max
        # what should we optimize? -> Time, Manuevability -> largest thrust, imbalance thrust?
        # allow fast termination?
        system_port_name_list = ["capacity", "I_battery", "V_max", "I_required", "rho"]

        def system_assumption(vs):
            return [vs["rho"] == 1.225, ]
        def system_guarantee():
            pass

    def get_motor_propeller_contract():
        motor_propeller_port_name_list = ["rho", "omega_prop", "torque_prop", "thrust", "shaft_motor"]
        motor_propeller_property_name_list = ["C_p", "C_t", "diameter", "shaft_prop", "W_prop"]

        def motor_propeller_assumption(vs):
            return [vs["shaft_prop"] >= vs["shaft_motor"], vs["C_p"] >= 0]

        def motor_propeller_guarantee(vs):
            return [
                vs["torque_prop"]
                == vs["C_p"] * vs["rho"] * vs["omega_prop"] ** 2 * vs["diameter"] ** 5 / (2 * 3.14159265) ** 3,
                vs["thrust"]
                == (vs["C_t"] * vs["rho"] * vs["omega_prop"] ** 2 * vs["diameter"] ** 4 / (2 * 3.14159265) ** 2),
                vs["omega_prop"] >= 0,
            ]

        motor_propeller_contract = ContractTemplate(
            name="Propeller",
            port_name_list=motor_propeller_port_name_list,
            property_name_list=motor_propeller_property_name_list,
            guarantee=motor_propeller_guarantee,
            assumption=motor_propeller_assumption,
        )
        return motor_propeller_contract

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


if __name__ == "__main__":
    from sym_cps.representation.tools.parsers.parse import parse_library_and_seed_designs
    from sym_cps.representation.tools.parsers.parsing_prop_table import parsing_prop_table

    c_library, designs = parse_library_and_seed_designs()
    design_concrete, _ = designs["TestQuad"]
    selection = RefineComponentSelection(analysis_file=data_folder/"ComponentLibrary" /"component_selection_analysis"/ "motor_propeller_pair.json",library=c_library)
    selection.search(d_concrete=design_concrete)