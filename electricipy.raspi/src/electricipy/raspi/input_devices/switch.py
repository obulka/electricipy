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


This module contains the base class for GPIO control.
"""
# Standard Imports
from time import sleep

import pigpio

# Local Imports
from electricipy.raspi.gpio_controller import GPIOController


class Switch(GPIOController):
    """Base switch class"""

    def __init__(self, pin, normally_open, pin_high=True, pi_connection=None):
        """ Initialise the switch.

        Args:
            pin (int): The pin the switch is connected to.
            normally_open (bool): True if the circuit will be open when
                the switch is not being pressed.

        Keyword Args:
            pin_high (bool):
                If True, then connect one side of the switch to the
                specified pin and the other to ground through a load.
                Otherwise, connect one side to the specified pin and the
                other to 3.3V through a load.
            pi_connection (pigpio.pi):
                The connection to the raspberry pi. If not specified, we
                assume the code is running on a pi and use the local
                gpio.
        """
        super().__init__(pi_connection=pi_connection)

        self._pin = pin
        self._pin_high = pin_high
        self._normally_open = normally_open

        self._pi.set_pull_up_down(
            self._pin,
            pigpio.PUD_UP if self._pin_high else pigpio.PUD_DOWN,
        )

        self._pi.callback(self._pin, pigpio.FALLING_EDGE, self._on_falling_edge)
        self._pi.callback(self._pin, pigpio.RISING_EDGE, self._on_rising_edge)
        self._pi.callback(self._pin, pigpio.EITHER_EDGE, self._on_either_edge)

    def _on_rising_edge(self, pin, level, tick):
        """"""

    def _on_falling_edge(self, pin, level, tick):
        """"""

    def _on_either_edge(self, pin, level, tick):
        """"""

    @property
    def _pin_state(self):
        """bool: Whether or not the pin value is currently high."""
        return bool(self._pi.read(self._pin))

    @property
    def pressed(self):
        """bool: Whether or not the switch is currently pressed."""
        return self._pin_state ^ self._pin_high


class EmergencyStop(Switch):
    """"""

    def __init__(self, pin, devices, pin_high=True, pi_connection=None):
        """ Initialise the switch.

        Args:
            pin (int): The pin the switch is connected to.
            devices (list(GPIOController)): The devices to stop if this
                switch is pressed.

        Keyword Args:
            pin_high (bool):
                If True, then connect one side of the switch to the
                specified pin and the other to ground through a load.
                Otherwise, connect one side to the specified pin and the
                other to 3.3V through a load.
            pi_connection (pigpio.pi):
                The connection to the raspberry pi. If not specified, we
                assume the code is running on a pi and use the local
                gpio.
        """
        super().__init__(
            pin,
            False,
            pin_high=pin_high,
            pi_connection=pi_connection,
        )
        self._devices = devices

    def _on_either_edge(self, _, _, _):
        """"""
        for device in self._devices:
            device.stop()
