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

    # motor.move_at_speed_for_time(360, 60)

    motor.move_by_angle_in_time(720, 1)
    motor.move_by_angle_in_time(-720, 1)
    motor.move_by_angle_in_time(360 * 3, 1)

    # motor.step(10)

    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == "__main__":
    main()
