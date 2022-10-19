# Author: Sydney Whittington

import argparse
import json

from parse import *
from astropy.io import ascii


def parse_trim_state(f, turning=False):
    steady_state = {}
    if turning:
        # only parsing difference is more info here (also more table info)
        steady_state.update(parse("Objective steady state speed is UVW world = {speed:>g} {:>g} {:>g} m/s; PQR world =  {:>g} {:>g} {rotation:>g} rad/s", next(f).strip()).named)
        steady_state.update(parse("Turning radius {turning_radius:>g} m (positive means clockwise looking down), Rworld = {turning_rate:>g} radians/s", next(f).strip()).named)
    else:
        steady_state.update(parse("Objective steady state speed is UVW world = {speed:>g} {:>g} {:>g} m/s = {:>g} {:>g} {:>g} miles per hour", next(f).strip()).named)

    # TODO: capture iteration info
    while "Nonlinear" not in next(f):
        pass
    
    trim_state_table = []
    danger = []
    while "Battery" not in (line := next(f)):
        if "Warning" in line or "Caution" in line:
            danger.append(line.strip())
        else:
            trim_state_table.append(line)

    # format (a25, 6f17.8)
    # 25 char string, 6 17 digit floats
    trim_state_columns = [0] + [i for i in range(25, 6*17+25, 17)]
    trim_state_raw_info = ascii.read(trim_state_table, format='fixed_width_no_header', col_starts=trim_state_columns)
    
    trim_state_info, trim_state_errors = decode_trim_state_info(trim_state_raw_info)
    danger.extend(trim_state_errors)

    battery_info = []

    # may be multiple batteries
    while "Total" not in line:
        if "Warning" in line or "Caution" in line:
            danger.append(line.strip())
        else:
            # only two forms of this ("with warning" or valid)
            if (battery := parse("Battery # {number:>d} Current = {current:>g} amps,  Time to 20% charge remaining = {flight_seconds:>g} s,  Flight distance = {distance:>g} m", line.strip())) is None:
                battery = parse("Battery # {number:>d} Current = {current:>g} amps,  Time to 20% charge remaining = {flight_seconds:>g} s,  Flight distance = {distance:>g} m with warning", line.strip())
            battery_info.append(battery.named)
        
        # advancing last because the first line was the end of the previous table
        line = next(f)
    
    total_power = parse("Total power from batteries {batteries:>g} watts;  total power in motors {motors:>g} watts", line.strip()).named

    # TODO: controls table

    # skip to the end of the trim state
    while (line := next(f)) != "\n":
        pass

    trim_state = {}
    trim_state["steady_state"] = steady_state
    trim_state.update(trim_state_info)
    trim_state["batteries"] = battery_info
    trim_state["power"] = total_power
    trim_state["problems"] = danger

    return trim_state


def decode_trim_state_info(info):
    trim_state = {
        "wing_loads":[],
        "controls":[],
        "motor_rpms":[],
        "thrusts":[],
        "motor_amps":[],
    }
    errors = []

    for raw_row in info:
        # strip the structured array out of the row
        row = list(raw_row)
        contents = row[0]

        if "UVW world" in contents:
            trim_state["UVW world"] = row[1:4]
            trim_state["UVW body"] = row[4:7]
        elif "UVWdot" in contents:
            trim_state["UVWdot"] = row[1:4]
            trim_state["PQRdot"] = row[4:7]
        elif "Pitch angle" in contents:
            trim_state["pitch angle"] = row[1]
        elif "Thrust world" in contents:
            trim_state["thrust world"] = row[1:4]
            trim_state["thrust body"] = row[4:7]
        elif "Lift world" in contents:
            trim_state["lift world"] = row[1:4]
            trim_state["lift body"] = row[4:7]
        elif "Drag world" in contents:
            trim_state["drag world"] = row[1:4]
            trim_state["drag body"] = row[4:7]
        elif "Wing Ld" in contents:
            # these are always in order so no need to actually track indices, just the array length
            low, high = parse("Wing Ld(N) {:>d} - {:>d}", contents.strip())
            trim_state["wing_loads"].extend([value for value in row[1:(2+high-low)]])
        elif "Controls" in contents:
            low, high = parse("Controls {:>d} - {:>d}", contents.strip())
            trim_state["controls"].extend([value for value in row[1:(2+high-low)]])
        elif "Motor RPM" in contents:
            low, high = parse("Motor RPM {:>d} - {:>d}", contents.strip())
            trim_state["motor_rpms"].extend([value for value in row[1:(2+high-low)]])
        elif "Thrust (N)" in contents:
            low, high = parse("Thrust (N) {:>d} - {:>d}", contents.strip())
            trim_state["thrusts"].extend([value for value in row[1:(2+high-low)]])
        elif "Motor Amps" in contents:
            low, high = parse("Motor Amps {:>d} - {:>d}", contents.strip())
            trim_state["motor_amps"].extend([value for value in row[1:(2+high-low)]])
        elif "Warning" in contents:
            errors.append(contents)

    return trim_state, errors


def fdm_to_json(f):
    # variables are named like we have an IDE that autocompletes
        # NOTE: is it fine to hardcode the length of these fixed parts?
        for _ in range(17):
            next(f)

        motor_table = []
        while "lift and drag" not in (line := next(f)):
            motor_table.append(line)

        # format(a10, i2, 12f13.2)
        # 10-char string, 2-char int, 12 13-char floats
        motor_columns = [0, 10] + [i for i in range(12, 12*13+12, 13)]
        motor_column_names = [
            "Category",
            "Motor #",
            "omega (rad/s)",
            "omega (RPM)",
            "Voltage (Volts)",
            "Thrust (N)",
            "Torque (Nm)",
            "Power (Watts)",
            "Current (amps)",
            "Efficiency (%)",
            "Motor Max Power (watts)",
            "Motor Max Current (amps)",
            "Battery Peak Current (amps)",
            "Battery Continuous Current (amps)"
        ]
        motor_info = ascii.read(motor_table, format='fixed_width_no_header', col_starts=motor_columns, names=motor_column_names)

        # lift table
        lift_and_drag_column_names = ["Angle of Attack alpha (deg)"] + [f"{i:.2f} (m/s)" for i in range(5, 55, 5)]
        for _ in range(4):
            next(f)
        
        lift_table = []
        while "Drag force" not in (line := next(f)):
            lift_table.append(line)

        # format(f20.3,10f9.2)
        # 20 char float, 10 9-char floats
        lift_columns = [0] + [i for i in range(20, 10*9+20, 9)]
        lift_info = ascii.read(lift_table, format='fixed_width_no_header', col_starts=lift_columns, names=lift_and_drag_column_names)

        # drag table
        for _ in range(3):
            next(f)
        
        drag_table = []
        while (line := next(f)) != "\n":
            drag_table.append(line)

        # format(f20.3,10f9.2)
        # 20 char float, 10 9-char floats
        drag_columns = [0] + [i for i in range(20, 10*9+20, 9)]
        drag_info = ascii.read(drag_table, format='fixed_width_no_header', col_starts=drag_columns, names=lift_and_drag_column_names)


        # control channel assignments
        # NOTE: should we capture the number of channels (motors and wings) here?
        for _ in range(12):
            next(f)

        motor_controls = []
        wing_controls = []
        while (line := next(f)) != "\n":
            if (propeller := parse("Propeller motor {motor:>d} controlled by uc channel {channel:>d} and powered by battery {battery:>d}", line.strip())) is not None:
                motor_controls.append(propeller.named)
            elif (wing := parse("Wing {wing:>d} servo {servo:>d} controlled by uc channel {channel:>d} with bias {bias:>g}", line.strip())) is not None:
                wing_controls.append(wing.named)


        # downward force
        downward_force = parse("Downward force (N) = mg = {:>g}", next(f).strip()).fixed[0]


        # trim states
        for _ in range(8):
            next(f)
            
        level_trims = []
        for _ in range(51):
            level_trims.append(parse_trim_state(f, turning=False))


        # trim state summary table (is there anything that's not previously captured?)
        for _ in range(13):
            next(f)

        trims_summary_table = []
        while (line := next(f)) != "\n":
            trims_summary_table.append(line)

        # format (f11.2,3f12.2,6f11.2,3f10.3,5x,a7,2x,a3)
        # 11 digit float, 3 12 digit floats, 6 11 digit floats, 3 10 digit floats, padding, 7 char string, padding, 3 char string
        # errors are format (f11.2,36x,66x,30x,5x,f7.4,2x,1pe11.3)
        trims_summary_columns = [0, 11, 23, 35, 47, 58, 69, 80, 91, 102, 113, 123, 133, 143, 155]
        trims_summary_column_names = [
            "Lateral speed (m/s)",
            "Distance (m)",
            "Flight time (s)",
            "Pitch angle (deg)",
            "max uc (-)",
            "Thrust (N)",
            "Lift (N)",
            "Drag (N)",
            "Current (amps)",
            "Total power (watts)",
            "Frac amp (-)",
            "Frac Pow (-)",
            "Frac Current (-)",
            "Solving Method/Acc. Error",
            "ARE"
        ]
        trims_summary_info = ascii.read(trims_summary_table, format='fixed_width_no_header', 
            col_starts=trims_summary_columns, names=trims_summary_column_names)

        max_level_distance = parse("Of all cases, maximum no-warning distance was at speed {speed:>g} m/s with distance {distance:>g} m", next(f).strip()).named
        max_level_speed = parse("Of all cases, maximum no-warning speed was a speed of {speed:>g} m/s with distance {distance:>g} m", next(f).strip()).named


        # trim state metrics
        for _ in range(2):
            next(f)

        level_trim_metrics = {}
        while (line := next(f)) != "\n":
            metric, value = parse("{:S} {:>g}", line.strip())
            level_trim_metrics[metric] = value

        # turning trim states
        # clockwise first
        for _ in range(7):
            next(f)

        clockwise_trims = []
        for _ in range(50):
            clockwise_trims.append(parse_trim_state(f, turning=True))

        # turning trim state summary table
        for _ in range(13):
            next(f)

        clockwise_trims_summary_table = []
        while (line := next(f)) != "\n":
            clockwise_trims_summary_table.append(line)

        # format (f11.2,3f12.2,7f10.2,3f10.3,5x,a7,2x,a3) 
        # only difference from level trims is the 4th one
        # 11 digit float, 3 12 digit floats, 7 10 digit floats, 3 10 digit floats, padding, 7 char string, padding, 3 char string
        # errors are still format (f11.2,36x,66x,30x,5x,f7.4,2x,1pe11.3)
        clockwise_trims_summary_columns = [0, 11, 23, 35, 47, 57, 67, 77, 87, 97, 107, 117, 127, 137, 147, 159] 
        clockwise_trims_summary_column_names = [
            "Tangent speed (m/s)",
            "Distance (m)",
            "Flight time (s)",
            "Pitch angle (deg)",
            "Roll angle (deg)",
            "max uc (-)",
            "Thrust (N)",
            "Lift (N)",
            "Drag (N)",
            "Current (amps)",
            "Total power (watts)",
            "Frac amp (-)",
            "Frac Pow (-)",
            "Frac Current (-)",
            "Solving Method/Acc. Error",
            "ARE"
        ]
        clockwise_trims_summary_info = ascii.read(clockwise_trims_summary_table, format='fixed_width_no_header', 
            col_starts=clockwise_trims_summary_columns, names=clockwise_trims_summary_column_names)

        max_clockwise_distance = parse("Of all cases, maximum no-warning distance was at speed {speed:>g} m/s with distance {distance:>g} m", next(f).strip()).named
        max_clockwise_speed = parse("Of all cases, maximum no-warning speed was a speed of {speed:>g} m/s with distance {distance:>g} m", next(f).strip()).named


        # clockwise trim state metrics
        for _ in range(2):
            next(f)

        clockwise_trim_metrics = {}
        while (line := next(f)) != "\n":
            metric, value = parse("{:S} {:>g}", line.strip())
            clockwise_trim_metrics[metric] = value


        # then counterclockwise (these are the same otherwise)
        for _ in range(7):
            next(f)

        counterclockwise_trims = []
        for _ in range(50):
            counterclockwise_trims.append(parse_trim_state(f, turning=True))

        for _ in range(15):
            next(f)

        counterclockwise_trims_summary_table = []
        while (line := next(f)) != "\n":
            counterclockwise_trims_summary_table.append(line)

        counterclockwise_trims_summary_columns = [0, 11, 23, 35, 47, 57, 67, 77, 87, 97, 107, 117, 127, 137, 147, 159] 
        counterclockwise_trims_summary_column_names = [
            "Tangent speed (m/s)",
            "Distance (m)",
            "Flight time (s)",
            "Pitch angle (deg)",
            "Roll angle (deg)",
            "max uc (-)",
            "Thrust (N)",
            "Lift (N)",
            "Drag (N)",
            "Current (amps)",
            "Total power (watts)",
            "Frac amp (-)",
            "Frac Pow (-)",
            "Frac Current (-)",
            "Solving Method/Acc. Error",
            "ARE"
        ]
        counterclockwise_trims_summary_info = ascii.read(counterclockwise_trims_summary_table, format='fixed_width_no_header', 
            col_starts=counterclockwise_trims_summary_columns, names=counterclockwise_trims_summary_column_names)

        max_counterclockwise_distance = parse("Of all cases, maximum no-warning distance was at speed {speed:>g} m/s with distance {distance:>g} m", next(f).strip()).named
        max_counterclockwise_speed = parse("Of all cases, maximum no-warning speed was a speed of {speed:>g} m/s with distance {distance:>g} m", next(f).strip()).named

        for _ in range(2):
            next(f)

        counterclockwise_trim_metrics = {}
        while (line := next(f)) != "\n":
            metric, value = parse("{:S} {:>g}", line.strip())
            counterclockwise_trim_metrics[metric] = value


        # flight trajectory info
        path_performance = {}
        for _ in range(1):
            next(f)

        flight_path = parse("Path performance, flight path {:>d}", next(f).strip()).fixed[0]
        selected_trim = parse("Initialized to lateral trim state {:>g}", next(f).strip()).fixed[0]
        path_performance["flight_path"] = flight_path
        path_performance["selected_trim"] = selected_trim

        for _ in range(5):
            next(f)

        trajectory_table = []
        while (line := next(f)) != "\n":
            trajectory_table.append(line)
            
        # format (16f10.3)
        # 16 10 digit floats
        trajectory_table_columns = [i for i in range(0, 16*10, 10)] 
        trajectory_table_column_names = [
            "time (s)",
            "phi (deg)",
            "theta (deg)",
            "psi (deg)",
            "Unorth (m/s)",
            "Veast (m/s)",
            "Wdown (m/s)",
            "Xnorth (m)",
            "Yeast (m)",
            "Zdown (m)",
            "Vt (m/s)",
            "alpha (deg)",
            "beta (deg)",
            "Thrust (N)",
            "Lift (N)",
            "Drag (N)"
        ]
        trajectory_table_info = ascii.read(trajectory_table, format='fixed_width_no_header', 
            col_starts=trajectory_table_columns, names=trajectory_table_column_names)


        flight_time, termination_cause = parse("Calculation completed at time {:^g} due to {}.", next(f).strip()).fixed
        path_performance["flight_time"] = flight_time
        path_performance["termination_cause"] = termination_cause

        for _ in range(2):
            next(f)

        battery_usage = []
        motor_usage = []
        while (line := next(f)) != "\n":
            if (battery := parse("Battery {battery:^d} fraction capacity used {capacity_used:>g} and fraction max continuous amperage used {amperage_used:>g}", line.strip())) is not None:
                battery_usage.append(battery.named)
            elif (motor := parse("Motor {motor:>d} fraction max amps reached {max_amps:>g} and fraction max power reached {max_power:>g}", line.strip())) is not None:
                motor_usage.append(motor.named)
        path_performance["battery_usage"] = battery_usage
        path_performance["motor_usage"] = motor_usage

        # wind speed and air density
        for _ in range(6):
            next(f)

        while "Final score" not in (line := next(f)):
            # scoring algorithms are different for each
            # and potential "you ignored electrical" type statements
            pass

        score = parse("Final score (rounded) = {:>g}", line.strip()).fixed[0]
        path_performance["score"] = score

        for _ in range(3):
            next(f)

        if ("not" in next(f)):
            path_success = False
        else:
            path_success = True
        path_performance["path_success"] = path_success
        
        for _ in range(2):
            next(f)
            
        path_metrics = {}
        try:
            while (line := next(f)) != "\n":
                # multiple values for some metrics
                if (metric_values := parse("{:S} {:>g}", line.strip())) is not None:
                    metric, value = metric_values
                elif (metric_values := parse("{:S} {:>g} {:>g} {:>g}", line.strip())) is not None:
                    metric, *value = metric_values
                elif (metric_values := parse("{:S} {:>g} {:>g} {:>g} {:>g} {:>g}", line.strip())) is not None:
                    metric, *value = metric_values
                path_metrics[metric] = value
        # we've finally reached the end of the file
        except StopIteration:
            pass


        complete = {}
        complete["motor_info"] = motor_info.to_pandas().to_dict(orient="records")
        complete["lift_info"] = lift_info.to_pandas().to_dict(orient="records")
        complete["drag_info"] = drag_info.to_pandas().to_dict(orient="records")
        complete["motor_controls"] = motor_controls
        complete["wing_controls"] = wing_controls
        complete["downward_force"] = downward_force

        complete["level_trims"] = level_trims
        complete["trims_summary"] = trims_summary_info.to_pandas().to_dict(orient="records")
        complete["max_level_distance"] = max_level_distance
        complete["max_level_speed"] = max_level_speed
        complete["level_trim_metrics"] = level_trim_metrics

        complete["clockwise_trims"] = clockwise_trims
        complete["clockwise_trims_summary"] = clockwise_trims_summary_info.to_pandas().to_dict(orient="records")
        complete["max_clockwise_distance"] = max_clockwise_distance
        complete["max_clockwise_speed"] = max_clockwise_speed
        complete["clockwise_trim_metrics"] = clockwise_trim_metrics

        complete["counterclockwise_trims"] = counterclockwise_trims
        complete["counterclockwise_trims_summary"] = counterclockwise_trims_summary_info.to_pandas().to_dict(orient="records")
        complete["max_counterclockwise_distance"] = max_counterclockwise_distance
        complete["max_counterclockwise_speed"] = max_counterclockwise_speed
        complete["counterclockwise_trim_metrics"] = counterclockwise_trim_metrics

        complete["flight_trajectory"] = trajectory_table_info.to_pandas().to_dict(orient="records")
        complete["path_metrics"] = path_metrics
        complete["path_performance"] = path_performance

        return complete


def main():
    parser = argparse.ArgumentParser(description="FDM to JSON parser")
    parser.add_argument('--version', action='version', version="fdm_to_json v0.1.0")
    parser.add_argument("input_file", help="Path to the FDM output file to be parsed")
    parser.add_argument("-o", "--output_file", help="Path to the JSON output file to write it to")

    args = parser.parse_args()
    with open(args.input_file, "r") as f:
        complete = fdm_to_json(f)

    if args.output_file is not None:
        with open(args.output_file, "w") as o:
            json.dump(complete, o) 
    else:
        print(json.dumps(complete))


if __name__ == "__main__":
    main()