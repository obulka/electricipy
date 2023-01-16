# 3rd Party Imports
import gpiozero

# Local Imports
from ..gpio_controller import GPIOManager


class SG90(gpiozero.AngularServo):
    """"""

    def __init__(self, pin):
        """"""
        super(SG90, self).__init__(
            pin=pin,
            min_angle=-90,
            max_angle=90,
            min_pulse_width=450 / 1000000,
            max_pulse_width=2450 / 1000000,
            pin_factory=gpiozero.pins.pigpio.PiGPIOFactory('127.0.0.1'),
        )


class HK15148B(gpiozero.AngularServo):
    """"""

    def __init__(self, pin):
        """"""
        super(HK15148B, self).__init__(
            pin=pin,
            min_angle=-45,
            max_angle=45,
            pin_factory=gpiozero.pins.pigpio.PiGPIOFactory('127.0.0.1'),
        )


class ServoMotorManager(GPIOManager):
    """ Manage multiple servo motors """

    @classmethod
    def sg90_manager(cls, servo_pins):
        """ Shortcut to initialize a manager of multiple HXT900 servo
        controllers.

        Args:
            servo_pins (list(int)): The servo pin numbers to use.

        Returns:
            ServoMotorManager: The servo motor manager.
        """
        motors = []
        for servo_pin in servo_pins:
            motors.append(SG90(servo_pin))
        return cls(motors)

    @classmethod
    def hk15148b_manager(cls, servo_pins):
        """ Shortcut to initialize a manager of multiple HXT900 servo
        controllers.

        Args:
            servo_pins (list(int)): The servo pin numbers to use.

        Returns:
            ServoMotorManager: The servo motor manager.
        """
        motors = []
        for servo_pin in servo_pins:
            motors.append(HK15148B(servo_pin))
        return cls(motors)

