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
# 3rd Party Imports
import pigpio


class GPIOController:
    """ Base class for gpio control. """

    def __init__(self, pi_connection=None):
        """ Initialize the controller.

        Keyword Args:
            pi_connection (pigpio.pi):
                The connection to the raspberry pi. If not specified, we
                assume the code is running on a pi and use the local
                gpio.

        Raises:
            ValueError:
                If a raspberry pi connection cannot be established.
        """
        self._pi = pi_connection if pi_connection else pigpio.pi()
        if not self._pi.connected:
            raise ValueError("Unable to connect to a raspberry pi.")

        self._stop = False

    def __enter__(self):
        """ Setup for whatever control routine the child implements. """
        self._initialize_gpio()
        self._stop = False

    def __exit__(self, exception_type, exception_value, exception_traceback):
        """ Exit and clean up after the routine.

        Args:
            exception_type (Exception): Indicates class of exception.
            exception_value (str): Indicates the type of exception.
            exception_traceback (traceback):
                Report which has all of the information needed to solve
                the exception.
        """
        self._cleanup_gpio()

    def _initialize_gpio(self):
        """ Initialize the GPIO pins. """

    def _cleanup_gpio(self):
        """ Reset all pins to cleanup. """

    def stop(self):
        """ Stops the current routine immediately. """
        self._stop = True


class GPIOManager:
    """ Base class for managing multile gpio controllers. """

    def __init__(self, controllers):
        """ Initialize the manager.

        Args:
            controllers (list(GPIOController)):
                The controllers to manage.
        """
        self._controllers = controllers

    def __getitem__(self, index):
        return self._controllers[index]

    def __len__(self):
        return len(self._controllers)
