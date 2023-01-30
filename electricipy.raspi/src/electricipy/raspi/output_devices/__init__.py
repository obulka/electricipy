from electricipy.raspi.gpio_controller import GPIOController


class OutputController(GPIOController):
    """"""

    def __init__(self, pins=pins, pi_connection=None):
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
        super().__init__(pins=pins, pi_connection=pi_connection)

    def _initialize_gpio(self):
        """ Initialize the GPIO pins. """
        for pin in self._pins:
            self._pi.set_mode(pin, pigpio.OUTPUT)
