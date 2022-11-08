import math

from sym_cps.representation.library.elements.library_component import LibraryComponent
from sym_cps.representation.library.elements.perf_table import PerfTable
from sym_cps.representation.tools.parsers.parse import parse_library_and_seed_designs
from sym_cps.representation.tools.parsers.parsing_prop_table import parsing_prop_table

# from sym_cps.contract.contract import Contract, ContractLibrary


def propeller_motor_g(
    i_motor,
    rho,
    speed,
    motor: LibraryComponent,
    propeller: LibraryComponent,
    table_dict: dict[LibraryComponent, PerfTable],
) -> tuple[float, float, float]:
    """return the thrust and voltage of the motor given the input motor current
    Return: thrust, v_motor, weight, P_motor_max, I_motor_max
    """
    # ports get value
    R_w: float = motor.properties["INTERNAL_RESISTANCE"].value / 1000  # Ohm
    K_t: float = motor.properties["KT"].value
    K_v: float = motor.properties["KV"].value * (2 * math.pi) / 60  # rpm/V to rad/(V-sec)
    I_idle: float = motor.properties["IO_IDLE_CURRENT_10V"].value
    diameter: float = propeller.properties["DIAMETER"].value / 1000
    shaft_diameter_motor: float = motor.properties["SHAFT_DIAMETER"].value
    shaft_diameter_propeller: float = propeller.properties["SHAFT_DIAMETER"].value
    # print(table.get_value(rpm = 13000, v = 90, label="Cp"))
    table = table_dict[propeller]
    C_p: float = table.get_value(rpm=18000, v=speed, label="Cp")  # 0.0659
    C_t: float = table.get_value(rpm=18000, v=speed, label="Ct")  # 0.1319

    W_prop = propeller.properties["Weight"].value
    W_motor = motor.properties["WEIGHT"].value
    I_max = motor.properties["MAX_CURRENT"].value
    P_max = motor.properties["MAX_POWER"].value

    # check values
    print(
        f"R_w {R_w}, K_t {K_t}, K_v {K_v}, I_idle {I_idle}, diameter {diameter}",
        f"\nC_p {C_p}, C_t {C_t}, W_prop {W_prop}, W_motor {W_motor}, I_max {I_max}, P_max {P_max}",
    )
    # contracts
    if i_motor - I_idle < 0 or C_p < 0:
        omega: float = 0
    else:
        omega: float = math.sqrt((2 * math.pi) ** 3 * K_t * (i_motor - I_idle) / (C_p * rho * diameter**5))
    thrust: float = (C_t * rho * omega**2 * diameter**4) / ((2 * math.pi) ** 2)
    v_motor: float = i_motor * R_w + omega / K_v
    weight: float = W_prop + W_motor
    print(f"omege {omega}, thrust {thrust}, v_mototr {v_motor}, i_motor {i_motor}, weight {weight}")
    return (thrust, v_motor, weight, I_max, P_max, shaft_diameter_motor, shaft_diameter_propeller)


def battery_g(num_battery: int, battery: LibraryComponent) -> tuple[float, float, float]:
    """return capacity, i_battery"""
    capacity: float = battery.properties["CAPACITY"].value * num_battery / 1000  # mAh -> Ah
    weight: float = battery.properties["WEIGHT"].value * num_battery
    voltage: float = battery.properties["VOLTAGE"].value
    I_max: float = (battery.properties["CONT_DISCHARGE_RATE"].value) * capacity  # convert to mA

    return (capacity, weight, voltage, I_max)


def battery_controller_g(i_battery, num_out: int, battery_controller):
    """convert the i_battery to the current for all motor"""
    return [i_battery / num_out * 0.95] * num_out


def system_requirement_a(capacity: float) -> tuple[float, float, float]:
    """Requirement of the battery-motor-propeller system"""
    #  current (coming from the battery), speed, rho (air density  ! (kg/m^3))
    # Ah -> for 400s
    # return (96, 0, 1.225)
    return (capacity * 3600 / 400, 0, 1.225)


def system_requirement_g(
    thrusts: list,
    vs_motor: list,
    v_battery,
    i_battery,
    weights: list,
    I_max,
    is_motor,
    Is_motor_max,
    Ps_motor_max,
    shaft_motor,
    shaft_prop,
):
    """Requirement of the battery-motor-propeller system"""
    # 0. motor and propeller should match
    # if shaft_motor != shaft_prop:
    #     print("Unmatched motor/propeller")
    #     return False
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
    if any(
        v_motor * i_motor > P_motor_max for (v_motor, i_motor, P_motor_max) in zip(vs_motor, is_motor, Ps_motor_max)
    ):
        print("Motor Power Exceeds")
        print(Ps_motor_max, is_motor, vs_motor)
        return False
    if any(i_motor > I_motor_max for (i_motor, I_motor_max) in zip(is_motor, Is_motor_max)):
        print("Motor Current Exceeds")
        print(Is_motor_max, is_motor)
        return False

    return True


def objective(
    thrusts: list, vs_motor: list, v_battery, i_battery, weights: list, I_max, is_motor, Is_motor_max, Ps_motor_max
):
    weight_sum = sum(weights)
    thrust_sum = sum(thrusts)

    weight_margin = thrust_sum - weight_sum
    print(f"weight: {weight_sum}, thrust: {thrust_sum}")
    return weight_margin


def test_contract():
    """Loading Library and Seed Designs"""
    c_library, designs = parse_library_and_seed_designs()
    table_dict = parsing_prop_table(c_library)
    print(" ")
    """get topology and concrete"""
    design_concrete, design_topology = designs["TestQuad"]
    """get concrete component"""
    battery: LibraryComponent
    propeller: LibraryComponent
    motor: LibraryComponent
    battery_controller: LibraryComponent
    for component in design_concrete.components:
        if component.c_type.id == "Propeller":
            propeller = component.library_component
        if component.c_type.id == "Battery_UAV":
            battery = component.library_component
        if component.c_type.id == "Motor":
            motor = component.library_component
        if component.c_type.id == "BatteryController":
            battery_controller = component.library_component

    print("Init Component:")
    print(f"Propeller: {propeller.id}")
    print(f"Motor: {motor.id}")
    print(f"Battery: {battery.id}")
    print(f"BatteryController: {battery_controller.id}")

    """Instantiate the contract"""
    # check number of battery
    # create connection and contract
    num_batteries = 0
    num_propellers = 0
    num_motors = 0
    num_batt_controllers = 0
    for node in design_topology.nodes:
        c_type = node["c_type"]
        if c_type.id == "Propeller":
            num_propellers += 1
        elif c_type.id == "Battery_UAV":
            num_batteries += 1
        elif c_type.id == "Motor":
            num_motors += 1
        elif c_type.id == "BatteryController":
            num_batt_controllers += 1

    print(
        f"# Motor: {num_motors}, # Battery: {num_batteries}, # Propeller: {num_propellers}, # BatteryController: {num_batt_controllers}"
    )

    ret_val = check_contract(
        battery=battery,
        battery_controller=battery_controller,
        motor=motor,
        propeller=propeller,
        num_batteries=num_batteries,
        num_motors=num_motors,
        table_dict=table_dict,
    )
    # Loop should be inserted here, Now the platform is setup, design problem at this level is define
    """Select the component"""
    obj_val = 0
    best_battery = None
    best_motor = None
    best_propeller = None
    print(len(c_library.components_in_type["Battery_UAV"]))
    print(len(c_library.components_in_type["Motor"]))
    print(len(c_library.components_in_type["Propeller"]))
    for n_p, propeller in enumerate(c_library.components_in_type["Propeller"]):
        # if n_b > 20:
        #     break
        for n_m, motor in enumerate(c_library.components_in_type["Motor"]):
            # if n_m > 100:
            #     break
            for n_b, battery in enumerate(c_library.components_in_type["Battery_UAV"]):
                # if n_p > 200:
                #     break
                # get motor/propeller component
                # print(n_b, n_m, n_p, propeller.properties["SHAFT_DIAMETER"].value, motor.properties["SHAFT_DIAMETER"].value)
                if (
                    propeller.properties["SHAFT_DIAMETER"].value > motor.properties["SHAFT_DIAMETER"].value
                    or propeller.properties["SHAFT_DIAMETER"].value >= 30
                ):
                    continue
                # if propeller.properties["SHAFT_DIAMETER"].value != motor.properties["SHAFT_DIAMETER"].value:
                #     continue

                print("counter:", n_b * 20 * 100 + n_m * 100 + n_p)
                ret_val = check_contract(
                    battery=battery,
                    battery_controller=battery_controller,
                    motor=motor,
                    propeller=propeller,
                    num_batteries=num_batteries,
                    num_motors=num_motors,
                    table_dict=table_dict,
                )
                if obj_val < ret_val:
                    best_battery = battery
                    best_motor = motor
                    best_propeller = propeller
                    obj_val = ret_val

    print("Best Component:")
    print(f"Propeller: {best_propeller.id}")
    print(f"Motor: {best_motor.id}")
    print(f"Battery: {best_battery.id}")
    print(f"BatteryController: {battery_controller.id}")
    ret_val = check_contract(
        battery=best_battery,
        battery_controller=battery_controller,
        motor=best_motor,
        propeller=best_propeller,
        num_batteries=num_batteries,
        num_motors=num_motors,
        table_dict=table_dict,
    )
    print(ret_val)


def check_contract(battery, battery_controller, motor, propeller, num_batteries, num_motors, table_dict):
    print(" ")
    print(f"Propeller: {propeller.id}")
    # print(f"Motor: {motor.id}")
    # print(f"Battery: {battery.id}")
    # print(f"BatteryController: {battery_controller.id}")
    print(" ")

    """get the template contract without knowing the component but know the topology"""

    def propeller_motor_g_inst(i_motor, rho, speed, motor, propeller):
        return propeller_motor_g(
            i_motor=i_motor, rho=rho, speed=speed, motor=motor, propeller=propeller, table_dict=table_dict
        )

    def battery_g_inst(battery):
        return battery_g(num_battery=num_batteries, battery=battery)

    def battery_controller_g_inst(i_battery, battery_controller):
        return battery_controller_g(i_battery=i_battery, num_out=num_motors, battery_controller=battery_controller)

    # skipped for this example as we know that the
    """get targeted environment"""
    # using the knowledge that there is only one target environment if we know the capacity
    capacity, weight, voltage, I_max = battery_g_inst(battery=battery)
    # print("Capacity: ", capacity)
    i_battery, speed, rho = system_requirement_a(capacity=capacity)
    """check contract satisfaction"""
    is_motor = battery_controller_g_inst(i_battery=i_battery, battery_controller=battery_controller)

    thrusts = []
    vs_motor = []
    weights = [weight]
    Is_motor_max = []
    Ps_motor_max = []

    for i_motor in is_motor:
        (thrust, v_motor, weight, I_motor_max, P_motor_max, shaft_motor, shaft_prop) = propeller_motor_g_inst(
            i_motor=i_motor, rho=rho, speed=speed, motor=motor, propeller=propeller
        )
        thrusts.append(thrust)
        vs_motor.append(v_motor)
        weights.append(weight)
        Is_motor_max.append(I_motor_max)
        Ps_motor_max.append(P_motor_max)

    """Check objective and System Contracts"""
    if system_requirement_g(
        thrusts=thrusts,
        vs_motor=vs_motor,
        v_battery=voltage,
        i_battery=i_battery,
        weights=weights,
        I_max=I_max,
        is_motor=is_motor,
        Is_motor_max=Is_motor_max,
        Ps_motor_max=Ps_motor_max,
        shaft_motor=shaft_motor,
        shaft_prop=shaft_prop,
    ):
        print("Contract Satisfied")
        obj_val = objective(
            thrusts=thrusts,
            vs_motor=vs_motor,
            v_battery=voltage,
            i_battery=i_battery,
            weights=weights,
            I_max=I_max,
            is_motor=is_motor,
            Is_motor_max=Is_motor_max,
            Ps_motor_max=Ps_motor_max,
        )
    else:
        print("Contract UnSatisfied")
        obj_val = -100

    return obj_val

    # Contract()

    # for multiple battery, what we can do is to stack them -> capacity double, I_peak doubles, weights double,
    # Since the current is expressed by C-rate, so it automatically doubles as capcity.


# def build_contract_library():
#     """Loading Library and Seed Designs"""
#     c_library, designs = parse_library_and_seed_designs()
#     print(" ")
#     # build library
#     contract_library = ContractLibrary()
#     propeller_motor_ctype = CType("Propeller_Motor")
#     contract = Contract(assume=True, guarantee=lambda i_in: )
#     requirement = Contract(assume = )
#     for ctype in c_library.component_types.values():
#         print(ctype.id)
#         if ctype.id == "Propeller":
#             contract = Contract(assume=True, guarantee=True)
#         if ctype.id == "Battery_UAV":
#             contract = Contract(assume=True, guarantee=True)
#         if ctype.id == "Motor":
#             pass
#         contract_library.addContract(ctype, )
#         #     Contract()

#     # apply library based on topology to create connection between contracts

#     # select the best component


if __name__ == "__main__":
    test_contract()
    # build_contract_library()
