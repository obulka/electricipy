#!/usr/bin/env python3
""" Testing
"""
# Standard Imports
import time

# 3rd Party Imports
import RPi.GPIO as GPIO

# Local Imports
from pilectric.motor_control import stepper


def main():
    num_full_steps_per_cycle = 200
    step_pin = 3
    direction_pin = 5
    enable_pin = 7
    microstep_pins = [10, 8]

    motor = stepper.TMC2209(
        step_pin,
        direction_pin,
        enable_pin,
        microstep_pins=microstep_pins,
        microsteps=8,
    )

    for step_cycle in range(3): 
        motor.move_motor_in_time(180., 1.)
        time.sleep(1)


if __name__ == "__main__":
    main()
