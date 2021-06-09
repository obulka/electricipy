""" This module contains stepper motor controls. """
# pylint: disable=no-member

# Standard Imports
import time

# 3rd Party Imports
import RPi.GPIO as GPIO

# Local Imports
from ..signals.waveforms.pwm import PWM

class StepperMotorController:
    """ Base class for control of stepper motors. """

    MICROSTEPS = {}
    FULL_STEPS_PER_TURN = None

    def __init__(self, step_pin, direction_pin, microstep_pins=(), microsteps=1):
        """ Stepper motor control class.

        Note: Uses BCM mode for compatibility with pigpio.

        Args:
            step_pin (int): The step pin number to use.
            direction_pin (int): The direction pin number to use.

        Keyword Args:
            microstep_pins (tuple(int,)):
                The pin numbers for the microstep settings. (MS2, MS1)
            microsteps (int):
                The number of microsteps to perform. If you have hard
                wired the microstep pins you must pass the number of
                microsteps you have set it to in order for the
                controller to operate correctly. The default 1 microstep
                means the motor is taking full steps.
        """
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        self._step_pin = step_pin
        self._direction_pin = direction_pin
        self._microstep_pins = microstep_pins

        self._microsteps = microsteps

        self._stop_motor = False
        self._clockwise = True

    @property
    def clockwise(self):
        """ bool: True if motor set to rotate clockwise, False if
        counterclockwise.
        """
        return self._clockwise

    @clockwise.setter
    def clockwise(self, rotate_clockwise):
        self._clockwise = rotate_clockwise

    @property
    def microsteps(self):
        """ int: The number of microsteps to take. """
        return self._microsteps

    @microsteps.setter
    def microsteps(self, microsteps):
        self._check_microstep_value(microsteps)
        self._microsteps = microsteps

    def _check_microstep_value(self, microsteps):
        """ Check if a number of microsteps is a valid option.

        Raises:
            ValueError: If the number of microsteps is invalid.
        """
        if microsteps not in self.MICROSTEPS:
            raise ValueError(
                f"Invalid number of microsteps: {microsteps}\n"
                f"Valid options are {self.MICROSTEPS.keys()}"
            )

    def _initialize_gpio(self):
        """ Initialize the GPIO pins. """
        GPIO.setup(self._step_pin, GPIO.OUT)
        GPIO.setup(self._direction_pin, GPIO.OUT)
        GPIO.output(self._direction_pin, not self._clockwise)

        microstep_pin_values = self.MICROSTEPS[self._microsteps]
        for pin, pin_value in zip(self._microstep_pins, microstep_pin_values):
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, pin_value)

    def _cleanup_gpio(self):
        """ Reset all pins to low to cleanup. """
        GPIO.output(self._step_pin, False)
        GPIO.output(self._direction_pin, False)

        for pin in self._microstep_pins:
            GPIO.output(pin, False)

    def stop(self):
        """ Stops the current motor routine immediately. """
        self._stop_motor = True

    def step_motor(self, num_steps, step_delay=5e-4):
        """ Step the motor a number of times.

        Note that this method guarantees the correct number of steps but
        does not guarantee that the time will be accurate due to the
        limitations of the operating system.

        Args:
            num_steps (int): Number of steps to perform.

        Keyword Args:
            step_delay (float):
                The time for which the pulse is high. Therefore one step
                will take 2 * step_delay seconds.
        """
        self._stop_motor = False

        self._initialize_gpio()

        try:
            for _ in range(num_steps):
                if self._stop_motor:
                    return

                GPIO.output(self._step_pin, True)
                time.sleep(step_delay)

                GPIO.output(self._step_pin, False)
                time.sleep(step_delay)

        finally:
            self._cleanup_gpio()

    def _angle_to_steps(self, angle):
        """ Convert a number of degrees to the closest number of steps.

        Args:
            angle (float): The number of degrees.

        Returns:
            int: The equivalent number of steps.
        """
        return round(self.FULL_STEPS_PER_TURN * self._microsteps * angle / 360.)

    def _speed_to_step_delay(self, speed):
        """ Convert a speed to the time a step pulse should be held high.

        Args:
            speed (float): The speed in degrees/second.

        Returns:
            float: The equivalent pulse time.
        """
        return 180. / (self.FULL_STEPS_PER_TURN * self._microsteps * speed)

    def move_motor_by_angle_at_speed(self, angle, speed):
        """ Move the motor a number of degrees at a speed.

        Note that this method guarantees the correct number of degrees but
        does not guarantee that the time will be accurate due to the
        limitations of the operating system.

        Args:
            angle (float): Number of degrees to move.
            speed (float): Speed in degrees/second to move at.
        """
        steps = self._degrees_to_steps(angle)
        step_delay = self._speed_to_step_delay(speed)

        self.step_motor(steps, step_delay)

    def move_motor_by_angle_in_time(self, angle, seconds):
        """ Move the motor a number of degrees in a period of time.

        Note that this method guarantees the correct number of degrees but
        does not guarantee that the time will be accurate due to the
        limitations of the operating system.

        Args:
            angle (float): Number of degrees to move.
            time (float): Time in which to move the motor by degrees.
        """
        self.move_motor_at_speed(angle, angle / seconds)

    def move_motor_at_speed_for_time(self, speed, seconds):
        """ Move the motor a number of degrees in a period of time.

        Note that this method guarantees the correct speed but
        does not guarantee that the time will be accurate due to the
        limitations of the operating system.

        Args:
            speed (float): Speed in degrees/second to move at.
            time (float): Time to move the motor for.
        """
        pwm = PWM((self._step_pin,))
        pwm.period = self._speed_to_step_delay(speed) * 2
        pwm.set_pulse_length_in_percentage(self._step_pin, 0.5)
        pwm.update()
        time.sleep(seconds)
        pwm.stop()


class TMC2209(StepperMotorController):
    """ Control a stepper motor using a TMC2209 v1.2 control board """

    MICROSTEPS = {
        8: (False, False),
        32: (False, True),
        64: (True, False),
        16: (True, True),
    }

    FULL_STEPS_PER_TURN = 200

    def __init__(
            self,
            step_pin,
            direction_pin,
            enable_pin,
            microstep_pins=(),
            microsteps=8):
        """ Initialize the pin locations.

        Note: Uses BOARD mode for compatibility with more Pi versions.

        Args:
            step_pin (int): The step pin number to use. (STEP)
            direction_pin (int): The direction pin number to use. (DIR)
            enable_pin (int): The enable pin number to use. (EN)

        Keyword Args:
            microstep_pins (tuple(int, int)):
                The pin numbers for the microstep settings. (MS2, MS1)
            microsteps (int):
                The number of microsteps to perform. If you have hard
                wired the microstep pins you must pass the number of
                microsteps you have set it to in order for the
                controller to operate correctly.
        """
        if len(microstep_pins) > 2:
            raise ValueError(
                "Too many microstep pins specified, there are only two."
            )

        self._check_microstep_value(microsteps)

        super().__init__(
            step_pin,
            direction_pin,
            microstep_pins=microstep_pins,
            microsteps=microsteps,
        )

        self._enable_pin = enable_pin

    def _initialize_gpio(self):
        super()._initialize_gpio()

        GPIO.setup(self._enable_pin, GPIO.OUT)
        GPIO.output(self._enable_pin, False)

    def _cleanup_gpio(self):
        super()._cleanup_gpio()

        GPIO.output(self._enable_pin, True)
