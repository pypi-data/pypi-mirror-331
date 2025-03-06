"""
 Latest update: 04-09-2023

 This code example is in the public domain.
 http://www.botnroll.com

IMPORTANT!!!!
Before you use this example you MUST calibrate the line sensor.
Run line_sensor_calibration.py (in calibration folder) first!
Line reading provides a linear value between -100 to 100

Line follow:
Motors speed varies using PID control.
Adjustable gains kp, ki and kd.
You can adjust the speed limit of the wheel that is outside the curve.
Press push button 3 (PB3) to enter control configuration menu.
"""

import os
import json
import time
import signal
from onepi.one import BnrOneAPlus

one = BnrOneAPlus(0, 0)  # object variable to control the Bot'n Roll ONE A+

max_linear_speed = 40
speed_boost = 3  # Curve outside wheel max speed limit
kp = 1.3
ki = 0.0013
kd = 0.35  # PID control gains
file_name = "config_line_follow_pid.json"
filename = os.path.join(os.path.dirname(__file__), file_name)

integral_error = 0.0  # Integral error
differential_error = 0.0  # Differential error
previous_proportional_error = 0  # Previous proportional eror
MAX_SPEED = 100.0


def wait_user_input():
    button = 0
    while button == 0:  # Wait a button to be pressed
        button = one.read_button()
    while one.read_button() != 0:  # Wait for button release
        pass
    return button


def set_max_speed(new_max_linear_speed):
    option = 0
    while option != 3:
        if option == 1:
            new_max_linear_speed += 1
        if option == 2:
            new_max_linear_speed -= 1
        new_max_linear_speed = cap_value(new_max_linear_speed, 0, 100)
        one.lcd1("   VelMax:", new_max_linear_speed)
        option = wait_user_input()
    return new_max_linear_speed


def set_speed_boost(new_speed_boost):
    option = 0
    while option != 3:
        if option == 1:
            new_speed_boost += 1
        if option == 2:
            new_speed_boost -= 1
        new_speed_boost = cap_value(new_speed_boost, 0, 20)
        one.lcd1(" Curve Boost:", new_speed_boost)
        option = wait_user_input()
    return new_speed_boost


def set_gain(new_gain, multiplier, increment, text, max_value, min_value=0):
    new_gain = int(new_gain * multiplier)
    max_value = max_value * multiplier
    option = 0
    while option != 3:
        if option == 1:
            new_gain += increment
            time.sleep(0.150)
        if option == 2:
            new_gain -= increment
            time.sleep(0.150)
        new_gain = cap_value(new_gain, min_value, max_value)
        one.lcd1(text + " Gain:", new_gain)
        option = wait_user_input()
    return new_gain / multiplier


def set_kp_gain(new_gain):
    return set_gain(new_gain, 1000, 10, " Kp", 10000)


def set_ki_gain(new_gain):
    return set_gain(new_gain, 10000, 1, " Ki", 100)


def set_kd_gain(new_gain):
    return set_gain(new_gain, 1000, 10, " Kd", 1000)


def config_menu():
    global max_linear_speed, speed_boost, kp, ki, kd
    one.lcd2("1:Menu")
    time.sleep(1)
    one.lcd2("1:++ 2:--   3:OK")

    max_linear_speed = set_max_speed(max_linear_speed)  # Maximum speed
    speed_boost = set_speed_boost(speed_boost)  # Outside wheel speed boost
    kp = set_kp_gain(kp)
    ki = set_ki_gain(ki)
    kd = set_kd_gain(kd)
    save_config(
        max_linear_speed, speed_boost, kp, ki, kd
    )  # Save values to configuration file


def main_screen():
    one.lcd1("Line Follow PID")
    one.lcd2("www.botnroll.com")


def menu():
    one.stop()
    while one.read_button() != 0:
        pass
    option = 0
    while option != 3:
        one.lcd1("Line Follow PID")
        one.lcd2("1:Menu   3:Start")
        option = wait_user_input()
        if option == 1:
            config_menu()
    one.lcd2("         3:Start")
    time.sleep(1)
    main_screen()


def load_config():
    """
    Read config values from file.
    max_linear_speed, speed_boost and gain
    """
    global max_linear_speed
    global speed_boost
    global kp
    global ki
    global kd

    try:
        with open(filename, "r") as file:
            data = json.load(file)
            # Access values from JSON file
            max_linear_speed = data["max_linear_speed"]
            speed_boost = data["speed_boost"]
            kp = data["kp"]
            ki = data["ki"]
            kd = data["kd"]

    except FileNotFoundError:
        # Handle the case when the file doesn't exist
        print(f"The file '{filename}' doesn't exist. Using default values.")


def save_config(new_max_linear_speed, new_speed_boost, new_kp, new_ki, new_kd):
    """
    Save config values to file.
    max_linear_speed, speed_boost and gain
    """
    data = {
        "max_linear_speed": new_max_linear_speed,
        "speed_boost": new_speed_boost,
        "kp": new_kp,
        "ki": new_ki,
        "kd": new_kd,
    }

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def cap_value(value, lower_limit, upper_limit):
    """
    Caps the value to lower and upper limits
    """
    if value < lower_limit:
        return lower_limit
    elif value > upper_limit:
        return upper_limit
    else:
        return value


def setup():
    one.set_min_battery_V(10.5)  # safety voltage for discharging the battery
    one.stop()  # stop motors
    load_config()
    menu()


def loop():
    global integral_error
    global differential_error
    global previous_proportional_error

    line = one.read_line()  # Read the line sensor value [-100, 100]
    line_ref = 0  # Reference line value
    proportional_error = 0  # Proportional error
    output = 0.0  # PID control output

    proportional_error = line_ref - line  # Proportional error
    differential_error = (
        proportional_error - previous_proportional_error
    )  # Differential error
    output = (
        (kp * proportional_error) + (ki * integral_error) + (kd * differential_error)
    )

    # Clean integral error if line value is zero or if line signal has changed
    if (proportional_error * previous_proportional_error) <= 0:
        integral_error = 0.0

    if output > MAX_SPEED:
        output = MAX_SPEED  # Limit the output value
    elif output < -MAX_SPEED:
        output = -MAX_SPEED
    else:
        integral_error += (
            proportional_error  # Increment integral error if output is within limits
        )

    previous_proportional_error = proportional_error

    vel_m1 = max_linear_speed - output
    vel_m2 = max_linear_speed + output
    # Limit motors maximum and minimum speed
    vel_m1 = cap_value(vel_m1, -5, max_linear_speed + speed_boost)
    vel_m2 = cap_value(vel_m2, -5, max_linear_speed + speed_boost)

    print(
        " Line:",
        int(line),
        "   M1:",
        int(vel_m1),
        "   M2:",
        int(vel_m2),
        end="       \r",
    )
    one.move(vel_m1, vel_m2)

    # Configuration menu
    if one.read_button() == 3:
        menu()  # PB3 to enter menu


def main():

    # function to stop the robot on exiting with CTRL+C
    def stop_and_exit(sig, frame):
        one.stop()
        time.sleep(0.1)
        exit(0)

    signal.signal(signal.SIGINT, stop_and_exit)

    setup()
    while True:
        loop()


if __name__ == "__main__":
    main()
