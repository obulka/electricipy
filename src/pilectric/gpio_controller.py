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

    def __exit__(self, type, value, traceback):
        """ Exit the routine. """
        self._cleanup_gpio()

    def _initialize_gpio(self):
        """ Initialize the GPIO pins. """
        pass

    def _cleanup_gpio(self):
        """ Reset all pins to cleanup. """
        pass

    def stop(self):
        """ Stops the current routine immediately. """
        self._stop = True
