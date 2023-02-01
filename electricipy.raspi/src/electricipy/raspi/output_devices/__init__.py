# 3rd Party Imports
import pigpio

# Local Imports
from electricipy.raspi.gpio_controller import GPIOController


class OutputController(GPIOController):
    """"""

    def _initialize_gpio(self):
        """ Initialize the GPIO pins. """
        for pin in self._pins:
            self._pi.set_mode(pin, pigpio.OUTPUT)
