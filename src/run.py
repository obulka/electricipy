#!/usr/bin/env python3
""" Testing """
# Standard Imports
import time

# Local Imports
from pilectric.motor_control import stepper


def main():
    """ Run test """
    step_pin = 18
    direction_pin = 3
    enable_pin = 4
    microstep_pins = [15, 14]
    microsteps = 64

    motor = stepper.TMC2209(
        step_pin,
        direction_pin,
        enable_pin,
        microstep_pins=microstep_pins,
        microsteps=microsteps,
    )

    start_time = time.time()
    motor.move_at_speed_for_time(360, 60)
    # motor.move_by_angle_in_time(360. * 60, 60)
    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == "__main__":
    main()
