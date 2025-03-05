"""
 Latest update: 04-09-2023

 This code example is in the public domain.
 http://www.botnroll.com

IMPORTANT!!!!
Before you use this example you MUST calibrate the line sensor.
Run line_sensor_calibration.py (in calibration folder) first!

Line reading provides a linear value between -100 to 100
Line follow:
Motors speed varies according to a quadratic function.
Sinusoidal function gain must be adjusted.
You can adjust the speed limit of the wheel that is outside the curve.
Press push button 3 (PB3) to enter control configuration menu.
"""

import os
import math
import json
import time
import signal
from onepi.one import BnrOneAPlus

one = BnrOneAPlus(0, 0)  # object variable to control the Bot'n Roll ONE A+

max_linear_speed = 55
# function gain -> Lower Gain, higher output
gain = 40.0  #  function gain
speed_boost = 4  # Curve outside wheel max speed limit
file_name = "config_line_follow_cosine.json"
filename = os.path.join(os.path.dirname(__file__), file_name)


def wait_user_input():
    button = 0
    while button == 0:  # Wait a button to be pressed
        button = one.read_button()
    while one.read_button() != 0:  # Wait for button release
        pass
    return button


def load_config():
    """
    Read config values from file.
    max_linear_speed, speed_boost and gain
    """
    global max_linear_speed
    global speed_boost
    global gain
    try:
        with open(filename, "r") as file:
            data = json.load(file)
            # Access values from JSON file
            max_linear_speed = data["max_linear_speed"]
            speed_boost = data["speed_boost"]
            gain = data["gain"]

    except FileNotFoundError:
        # Handle the case when the file doesn't exist
        print(f"The file '{filename}' doesn't exist. Using default values.")


def save_config(new_max_linear_speed, new_speed_boost, new_gain):
    """
    Save config values to file.
    max_linear_speed, speed_boost and gain
    """
    data = {
        "max_linear_speed": new_max_linear_speed,
        "speed_boost": new_speed_boost,
        "gain": new_gain,
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


def set_linear_gain(new_gain):
    new_gain = int(new_gain)
    option = 0
    while option != 3:
        if option == 1:
            new_gain += 1
        if option == 2:
            new_gain -= 1
        new_gain = cap_value(new_gain, 0, 300)
        one.lcd1(" Line Gain:", new_gain)
        option = wait_user_input()
    return new_gain


def config_menu():
    global max_linear_speed, speed_boost, gain
    one.lcd2("1:Menu")
    time.sleep(1)
    one.lcd2("1:++ 2:--   3:OK")

    max_linear_speed = set_max_speed(max_linear_speed)  # Maximum speed
    speed_boost = set_speed_boost(speed_boost)  # Outside wheel speed boost
    gain = set_linear_gain(gain)  # Linear gain KLine
    save_config(
        max_linear_speed, speed_boost, gain
    )  # Save values to configuration file


def main_screen():
    one.lcd1("Line Follow Wave")
    one.lcd2("www.botnroll.com")


def menu():
    one.stop()
    while one.read_button() != 0:
        pass
    option = 0
    while option != 3:
        one.lcd1("Line Follow Wave")
        one.lcd2("1:Menu   3:Start")
        option = wait_user_input()
        if option == 1:
            config_menu()
    one.lcd2("         3:Start")
    time.sleep(1)
    main_screen()


def setup():
    one.min_battery(10.5)  # safety voltage for discharging the battery
    one.stop()  # stop motors
    load_config()  # read control values from file
    menu()


def loop():
    global gain, max_linear_speed, speed_boost
    vel_m1 = 0
    vel_m2 = 0
    line = one.read_line()
    if line <= 0:
        vel_m1 = max_linear_speed * math.cos(line / gain)  # function for motor 1
        vel_m2 = max_linear_speed + max_linear_speed - vel_m1
    else:
        vel_m2 = max_linear_speed * math.cos(line / gain)  # function for motor 2
        vel_m1 = max_linear_speed + max_linear_speed - vel_m2

    # Limit motors maximum and minimum speed
    vel_m1 = cap_value(vel_m1, -1, max_linear_speed + speed_boost)
    vel_m2 = cap_value(vel_m2, -1, max_linear_speed + speed_boost)

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
