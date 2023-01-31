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


This module contains stepper motor controls.
"""
# Standard Imports
import time

# 3rd Party Imports
import pigpio

# Local Imports
from electricipy.raspi.gpio_controller import GPIOManager

from .. import OutputController
from ..signals.waves import SquareWave


class StepperMotorController(OutputController):
    """ Base class for control of stepper motors. """

    _MICROSTEPS = {}
    _FULL_STEPS_PER_TURN = None

    def __init__(
            self,
            step_pin,
            direction_pin,
            microstep_pins,
            microsteps=1,
            gear_ratio=1.,
            pitch=None,
            pi_connection=None):
        """ Stepper motor control class.

        Note: Uses BCM mode for compatibility with pigpio.

        Args:
            step_pin (int): The step pin number to use.
            direction_pin (int): The direction pin number to use.
            microstep_pins (tuple(int,)): The pin numbers for the
                microstep settings. (MS2, MS1)

        Keyword Args:

            microsteps (int):
                The number of microsteps to perform. If you have hard
                wired the microstep pins you must pass the number of
                microsteps you have set it to in order for thecontroller
                to operate correctly. The default 1 microstep means the
                motor is taking full steps.
            gear_ratio (float): TODO
            pitch (float): TODO
            pi_connection (pigpio.pi):
                The connection to the raspberry pi. If not specified, we
                assume the code is running on a pi and use the local
                gpio.
        """
        self._step_pin = step_pin
        self._direction_pin = direction_pin
        self._microstep_pins = microstep_pins

        pins = (self._step_pin, self._direction_pin)
        for pin in self._microstep_pins:
            pins += (pin,)

        super().__init__(pins=pins, pi_connection=pi_connection)

        self._microsteps = microsteps

        self._counterclockwise = True
        self._wave = None

    @property
    def counterclockwise(self):
        """ bool: True if motor set to rotate counterclockwise, False if
        clockwise.
        """
        return self._counterclockwise

    @counterclockwise.setter
    def counterclockwise(self, rotate_counterclockwise):
        self._counterclockwise = rotate_counterclockwise

    @property
    def clockwise(self):
        """ bool: True if motor set to rotate clockwise, False if
        counterclockwise.
        """
        return not self._counterclockwise

    @clockwise.setter
    def clockwise(self, rotate_clockwise):
        self._counterclockwise = not rotate_clockwise

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
        if microsteps not in self._MICROSTEPS:
            raise ValueError(
                f"Invalid number of microsteps: {microsteps}\n"
                f"Valid options are {self._MICROSTEPS.keys()}"
            )

    def _initialize_gpio(self):
        """ Initialize the GPIO pins. """
        super()._initialize_gpio()

        self._pi.write(self._direction_pin, self._counterclockwise)

        microstep_pin_values = self._MICROSTEPS[self._microsteps]
        for pin, pin_value in zip(self._microstep_pins, microstep_pin_values):
            self._pi.write(pin, pin_value)

    def _cleanup_gpio(self):
        """ Reset all pins to low to cleanup. """
        self._pi.write(self._direction_pin, False)

        for pin in self._microstep_pins:
            self._pi.write(pin, False)

    def step(self, num_steps, step_period=1e-3):
        """ Step the motor a number of times.

        Args:
            num_steps (int): Number of steps to perform.

        Keyword Args:
            step_period (float): The period at which to drive the steps.
                One step will take step_period seconds to complete.
        """
        self._wave = SquareWave(
            self._step_pin,
            num_steps,
            pi_connection=self._pi,
            period=step_period,
        )
        with self, self._wave:
            # Wait for wave to finish transmission
            while self._pi.wave_tx_busy():
                if self._stop:
                    break
                time.sleep(step_period)

    def _angle_to_steps(self, angle):
        """ Convert a number of degrees to the closest number of steps.

        Args:
            angle (float): The number of degrees.

        Returns:
            int: The equivalent number of steps.
        """
        return round(self._FULL_STEPS_PER_TURN * self._microsteps * angle / 360.)

    def _angular_speed_to_step_speed(self, speed):
        """ Convert a speed in degrees/second to steps/second.

        Args:
            speed (float): The speed in degrees/second.

        Returns:
            float: The equivalent speed in steps/second.
        """
        return self._FULL_STEPS_PER_TURN * self._microsteps * speed / 360.

    def _angular_speed_to_step_period(self, speed):
        """ Convert a speed in degrees/second to the step delay
        (pulse period).

        Args:
            speed (float): The speed in degrees/second.

        Returns:
            float: The equivalent pulse time in seconds.
        """
        return 1 / (2 * self._angular_speed_to_step_speed(speed))

    def move_by_angle_at_speed(self, angle, speed):
        """ Move the motor a number of degrees at a speed.

        Args:
            angle (float): Number of degrees to move.
            speed (float): Speed in degrees/second to move at.
        """
        if angle < 0:
            self.clockwise = True
        else:
            self.counterclockwise = True
        steps = self._angle_to_steps(abs(angle))
        step_period = self._angular_speed_to_step_period(abs(speed))

        self.step(steps, step_period)

    def move_by_angle_in_time(self, angle, time):
        """ Move the motor a number of degrees in a period of time.

        Args:
            angle (float): Number of degrees to move.
            time (float): Time in which to move the motor by degrees.
        """
        self.move_by_angle_at_speed(angle, angle / time)

    def move_at_speed_for_time(self, speed, time):
        """ Move the motor a number of degrees in a period of time.

        Args:
            speed (float): Speed in degrees/second to move at.
            time (float): Time to move the motor for in seconds.
        """
        self.move_by_angle_at_speed(speed * time, speed)



class TMC2209(StepperMotorController):
    """ Control a stepper motor using a TMC2209 v1.2 control board """

    _MICROSTEPS = {
        8: (False, False),
        32: (False, True),
        64: (True, False),
        16: (True, True),
    }

    _FULL_STEPS_PER_TURN = 200

    def __init__(
            self,
            step_pin,
            direction_pin,
            enable_pin,
            microstep_pins=(),
            microsteps=8,
            pi_connection=None):
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
                microsteps you have set it to in order for thecontroller
                to operate correctly. The default 1 microstep means the
                motor is taking full steps.
            pi_connection (pigpio.pi):
                The connection to the raspberry pi. If not specified, we
                assume the code is running on a pi and use the local
                gpio.

        Raises:
            ValueError: If too many microstep pins are passed.
        """
        if len(microstep_pins) > 2:
            raise ValueError(
                "Too many microstep pins specified, there are only two.",
            )

        self._check_microstep_value(microsteps)

        super().__init__(
            step_pin,
            direction_pin,
            microstep_pins=microstep_pins,
            microsteps=microsteps,
            pi_connection=pi_connection,
        )

        self._enable_pin = enable_pin

    def _initialize_gpio(self):
        """ Initialize the GPIO pins. """
        super()._initialize_gpio()

        self._pi.set_mode(self._enable_pin, pigpio.OUTPUT)
        self._pi.write(self._enable_pin, False)

    def _cleanup_gpio(self):
        """ Reset all pins to low to cleanup. """
        super()._cleanup_gpio()

        self._pi.write(self._enable_pin, True)


class StepperMotorManager(GPIOManager):
    """ Manage multiple stepper motors """

    @classmethod
    def tmc2209_manager(
            cls,
            step_pins,
            direction_pins,
            enable_pins,
            microstep_pins,
            microsteps,
            pi_connections=None):
        """ Shortcut to initialize a manager of multiple TMC2209 v1.2
        motor controllers. Note that all of the argument lists must be
        the same length.

        Args:
            step_pins (list(int)): The step pin number to use. (STEP)
            direction_pins (list(int)):
                The direction pin number to use. (DIR)
            enable_pins (list(int)): The enable pin number to use. (EN)

        Keyword Args:
            microstep_pins (list(tuple(int, int))):
                The pin numbers for the microstep settings. (MS2, MS1)
            microsteps (list(int)):
                The number of microsteps to perform. If you have hard
                wired the microstep pins you must pass the number of
                microsteps you have set it to in order for thecontroller
                to operate correctly. The default 1 microstep means the
                motor is taking full steps.
            pi_connections (list(pigpio.pi)):
                The connection to the raspberry pi. If not specified, we
                assume the code is running on a pi and use the local
                gpio.
        """
        motors = []
        for step_pin, dir_pin, enable_pin, microstep_pin, microstep, pi_connection in zip(
                step_pins,
                direction_pins,
                enable_pins,
                microstep_pins,
                microsteps,
                pi_connections if pi_connections else (None,) * len(step_pins)):
            motors.append(
                TMC2209(
                    step_pin,
                    dir_pin,
                    enable_pin,
                    microstep_pin,
                    microsteps=microstep,
                    pi_connection=pi_connection,
                )
            )
        return cls(motors)

    def move_by_angles_at_speeds(self, angles, speeds):
        """ Move the motor a number of degrees at a speed.

        Args:
            angles (list(float)): Number of degrees to move.
            speeds (list(float)): Speeds in degrees/second to move at.
        """
        for motor_controller, angle, speed in zip(self._controllers, angles, speeds):
            motor_controller.move_by_angle_at_speed(angle, speed)

    def move_by_angles_in_times(self, angles, times):
        """ Move the motor a number of degrees in a period of time.

        Args:
            angles (float): Number of degrees to move.
            times (float): Time in which to move the motor by degrees.
        """
        for motor_controller, angle, time in zip(self._controllers, angles, times):
            motor_controller.move_by_angle_in_time(angle, time)

    def move_at_speeds_for_times(self, speeds, times):
        """ Move the motor a number of degrees in a period of time.

        Args:
            speeds (float): Speed in degrees/second to move at.
            times (float): Time to move the motor for in seconds.
        """
        for motor_controller, speed, time in zip(self._controllers, speeds, times):
            motor_controller.move_at_speed_for_time(speed, time)
