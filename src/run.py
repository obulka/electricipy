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
import time

# Local Imports
from pilectric.motor_control import stepper


def main():
    """ Run test """
    step_pins = [18, 13]
    direction_pins = [3, 27]
    enable_pins = [4, 17]
    microstep_pins = [[15, 14], [24, 23]]
    microsteps = [64, 64]

    motors = []
    for step_pin, dir_pin, enable_pin, microstep_pin, microstep in zip(
            step_pins,
            direction_pins,
            enable_pins,
            microstep_pins,
            microsteps):
        motors.append(
            stepper.TMC2209(
                step_pin,
                dir_pin,
                enable_pin,
                microstep_pins=microstep_pin,
                microsteps=microstep,
            )
        )

    start_time = time.time()

    # motor.move_at_speed_for_time(360, 60)

    for motor in motors:
        motor.move_by_angle_in_time(360, 1)
        motor.move_by_angle_in_time(-360, 1)
        motor.move_by_angle_in_time(720, 1)
        print("--- %s seconds ---" % (time.time() - start_time))

    # motor.step(10)


if __name__ == "__main__":
    main()
