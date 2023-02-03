#!/usr/bin/env python3
"""
Copyright 2021 Owen Bulka

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
# Standard Imports
import os
import time

# Local Imports
from electricipy.raspi.input_devices.switch import Switch
from electricipy.raspi.output_devices.motors import servo, stepper, brushless


def stepper_test():
    """"""
    motor_controller = stepper.StepperMotorController([
        stepper.TMC2209(
            step_pin=18,
            direction_pin=3,
            enable_pin=4,
            microstep_pins=(15, 14),
            microsteps=64,
            gear_ratio=1.,
            linear=True,
            pitch=5e-3,
        ),
        stepper.TMC2209(
            step_pin=13,
            direction_pin=27,
            enable_pin=17,
            microstep_pins=(24, 23),
            microsteps=64,
            gear_ratio=1.,
            linear=False,
        ),
    ])

    motor_controller.move_by_angles_in_time([-720, 320], 2)
    motor_controller.move_by_angles_in_time([720, -320], 2)
    motor_controller.move_by_angles_in_time([-720, 360], 2)
    motor_controller.move_by_angles_in_time([720, -360], 2)


def servo_test():
    """ Test some servos.

    You can find the max and min pulse width by repeatedly running:
    `pigs s [pin] [pulse width]` in a terminal, and changing the pulse
    width until the servo has moved to its limit, and backing off that
    pulse width limit still affects the servo position, then note the
    values.
    """
    servo_controller = servo.ServoController([
        servo.HK15148B(
            19,
            max_pulse_width=1225, # My servos don't like large pulse widths
        ),
        servo.SG90(
            20,
            max_pulse_width=1300,
        ),
    ])

    with servo_controller:
        servo_controller.go_to_positions([10, -10])
        time.sleep(5)
        servo_controller.go_to_positions([-10, 10])
        time.sleep(5)
        servo_controller.go_to_positions([20, -20])
        time.sleep(2)
        servo_controller.max()
        time.sleep(2)
        servo_controller.min()
        time.sleep(2)
        servo_controller.mid(0)
        time.sleep(2)


def esc_test():
    """"""
    esc = brushless.ElectronicSpeedController(19)
    with esc:
        esc.initialise()
        print("initialised")
        esc.mid()
        # esc.max()
        time.sleep(0.1)


def switch_test():
    """"""
    switch = Switch(5, True, pin_high=True)

    while True:
        time.sleep(1)
        print(switch.pressed)


def main():
    """ Script to test development """
    # os.system("sudo pigpiod -t0")

    start_time = time.time()

    stepper_test()
    # esc_test()
    # servo_test()
    # switch_test()

    print("--- %s seconds ---" % (time.time() - start_time))

    # motor.step(10)


if __name__ == "__main__":
    main()
