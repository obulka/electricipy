""" This module contains the base class for GPIO control. """
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
        """ Exit the routine.

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
