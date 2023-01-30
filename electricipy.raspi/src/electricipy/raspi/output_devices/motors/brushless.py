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
import multiprocessing
from time import sleep

# 3rd Party Imports
import pigpio

# Local Imports
from ..signals.pwm import PWMController


class ElectronicSpeedController(PWMController):
    """"""

    def __init__(
            self,
            pin,
            min_pulse_width=700,
            max_pulse_width=2000,
            initial_pulse_width=700,
            pi_connection=None):
        """"""
        super(ElectronicSpeedController, self).__init__(
            pin,
            min_pulse_width=min_pulse_width,
            max_pulse_width=max_pulse_width,
            initial_pulse_width=initial_pulse_width,
            pi_connection=pi_connection,
        )

    def initialise(self):
        """ Set the throttle to low so we can initialise the ESC. """
        print("Disconnect the battery and press Enter...")

        if input() != "":
            return

        self._pi.set_servo_pulsewidth(self._pin, self._min_pulse_width)

        print(
            "Connect the battery now.\n"
            "You will here the start-up tones, followed by a beep for each battery cell.\n"
            "You will then here a single long beep.\n"
            "Then press Enter..."
        )

        if input() != "":
            return
