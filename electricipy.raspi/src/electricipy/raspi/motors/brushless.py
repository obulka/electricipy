# Standard Imports
import multiprocessing
from time import sleep

# 3rd Party Imports
import pigpio #importing GPIO library

# Local Imports
from ..gpio_controller import GPIOController, GPIOManager

class ElectronicSpeedController(GPIOController):
    """"""

    def __init__(
            self,
            pin,
            min_pulse_width=700,
            max_pulse_width=2000,
            starting_pulse_width=1500,
            pi_connection=None):
        super(ElectronicSpeedController, self).__init__(pi_connection=pi_connection)

        self._pin = pin

        self._min_pulse_width = min_pulse_width
        self._max_pulse_width = max_pulse_width

        self._pulse_width = multiprocessing.Value("d", starting_pulse_width)

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

    def calibrate(self):
        """This is the auto-calibration procedure of an ESC."""
        with self:
            print("Disconnect the battery and press Enter\n")

            input_ = input()
            if input_ == "":
                self._pi.set_servo_pulsewidth(self._pin, self._max_pulse_width)
                print(
                    "Connect the battery now.\n"
                    "You will here two beeps, then a gradual falling tone.\n"
                    "Then press Enter\n")
                input_ = input()
                if input_ == '':            
                    self._pi.set_servo_pulsewidth(self._pin, self._min_pulse_width)
                    sleep(12)

                    self._pi.set_servo_pulsewidth(self._pin, 0)
                    sleep(2)

                    self._pi.set_servo_pulsewidth(self._pin, self._min_pulse_width)
                    sleep(1)

    def arm(self):
        """ Arm the ESC. """
        with self:
            print("Connect the battery and press Enter\n")

            input_ = input()
            if input_ == "":
                self._pi.set_servo_pulsewidth(self._pin, 0)
                sleep(1)

                self._pi.set_servo_pulsewidth(self._pin, self._max_pulse_width)
                sleep(1)

                self._pi.set_servo_pulsewidth(self._pin, self._min_pulse_width)
                sleep(1)

    def start(self):
        """"""
        self._pi.set_servo_pulsewidth(self._pin, self._pulse_width)

    def run_at_pulse_width_for_time(self, pulse_width, time):
        """"""
        self._pulse_width = pulse_width

        with self:
            self.start()
            sleep(time)
