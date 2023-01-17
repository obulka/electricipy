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


PWM Module
"""
# Standard Imports
from time import sleep

# 3rd Party Imports
import pigpio

# Local Imports
from electricipy.raspi.gpio_controller import GPIOController


class PWMController(GPIOController):
    """"""

    def __init__(
            self,
            pin,
            min_pulse_width=500,
            max_pulse_width=2500,
            initial_pulse_width=1500,
            pi_connection=None):
        super(PWMController, self).__init__(pi_connection=pi_connection)

        self._pin = pin

        self._min_pulse_width = min_pulse_width
        self._max_pulse_width = max_pulse_width

        self._pulse_width = initial_pulse_width

    @property
    def pulse_width(self):
        return self._pulse_width

    @pulse_width.setter
    def pulse_width(self, new_pulse_width):
        """"""
        self._pulse_width = max(
            min(new_pulse_width, self._max_pulse_width),
            self._min_pulse_width
        )

    def _initialize_gpio(self):
        """ Initialize the GPIO pins. """
        self._pi.set_servo_pulsewidth(self._pin, 0)

    def _cleanup_gpio(self):
        """ Reset all pins to cleanup. """
        self._pi.set_servo_pulsewidth(self._pin, 0)

    def start(self):
        """"""
        self._pi.set_servo_pulsewidth(self._pin, self._pulse_width)

    def min(self):
        """"""
        self.pulse_width = self._min_pulse_width
        self.start()

    def max(self):
        """"""
        self.pulse_width = self._max_pulse_width
        self.start()

    def mid(self):
        """"""
        self.pulse_width = (
            (self._max_pulse_width - self._min_pulse_width)
            / 2
            + self._min_pulse_width
        )
        self.start()

    def run_at_pulse_width_for_time(self, pulse_width, time):
        """"""
        self._pulse_width = pulse_width

        with self:
            self.start()
            sleep(time)
