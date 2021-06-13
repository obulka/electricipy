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
from .. import GPIOController


class StepperMotorController(GPIOController):
    """ Base class for control of stepper motors. """

    MICROSTEPS = {}
    FULL_STEPS_PER_TURN = None

    def __init__(
            self,
            step_pin,
            direction_pin,
            microstep_pins=(),
            microsteps=1,
            pi_connection=None):
        """ Stepper motor control class.

        Note: Uses BCM mode for compatibility with pigpio.

        Args:
            step_pin (int): The step pin number to use.
            direction_pin (int): The direction pin number to use.

        Keyword Args:
            microstep_pins (tuple(int,)): The pin numbers for the
                microstep settings. (MS2, MS1)
            microsteps (int):
                The number of microsteps to perform. If you have hard
                wired the microstep pins you must pass the number of
                microsteps you have set it to in order for thecontroller
                to operate correctly. The default 1 microstep means the
                motor is taking full steps.
        """
        super().__init__(pi_connection=pi_connection)

        self._step_pin = step_pin
        self._direction_pin = direction_pin
        self._microstep_pins = microstep_pins

        self._microsteps = microsteps

        self._counterclockwise = True
        self._wave_id = None

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
        if microsteps not in self.MICROSTEPS:
            raise ValueError(
                f"Invalid number of microsteps: {microsteps}\n"
                f"Valid options are {self.MICROSTEPS.keys()}"
            )

    def _initialize_gpio(self):
        """ Initialize the GPIO pins. """
        self._pi.set_mode(self._step_pin, pigpio.OUTPUT)
        self._pi.set_mode(self._direction_pin, pigpio.OUTPUT)
        self._pi.write(self._direction_pin, self._counterclockwise)

        microstep_pin_values = self.MICROSTEPS[self._microsteps]
        for pin, pin_value in zip(self._microstep_pins, microstep_pin_values):
            self._pi.set_mode(pin, pigpio.OUTPUT)
            self._pi.write(pin, pin_value)

    def _cleanup_gpio(self):
        """ Reset all pins to low to cleanup. """
        print("cleanup")
        if self._wave_id is not None:
            print("delete")
            self._pi.wave_delete(self._wave_id)
            self._wave_id = None

        self._pi.write(self._step_pin, False)
        self._pi.write(self._direction_pin, False)

        for pin in self._microstep_pins:
            self._pi.write(pin, False)

    def step(self, num_steps, step_delay=5e-4):
        """ Step the motor a number of times.

        Args:
            num_steps (int): Number of steps to perform.

        Keyword Args:
            step_delay (float): The time for which the pulse is high.
                Therefore one step will take 2 * step_delay seconds.
        """
        with self:
            microsecond_step_delay = round(1e6 * step_delay)

            self._pi.wave_add_generic([
                pigpio.pulse(1 << self._step_pin, 0, microsecond_step_delay),
                pigpio.pulse(0, 1 << self._step_pin, microsecond_step_delay),
            ])

            self._wave_id = self._pi.wave_create()

            full_loop_denominator = 256 * 255 + 255
            num_full_loops = num_steps // full_loop_denominator

            if num_full_loops > full_loop_denominator:
                raise ValueError("Too many steps for waveform.")

            full_loop_remainder = num_steps % full_loop_denominator

            final_multiple = full_loop_remainder // 256
            final_remainder = full_loop_remainder % 256

            wave_chain = [
                255, 0,
                    255, 0,
                        self._wave_id,
                    255, 1,
                    255, 255,
                255, 1,
                num_full_loops % 256, num_full_loops // 256,
            ]
            wave_chain.extend([
                255, 0,                          # Start loop
                    self._wave_id,               # Create wave
                255, 1,                          # loop end
                final_remainder, final_multiple, # repeat step_remainder + 256 * step_multiple
            ])

            self._pi.wave_chain(wave_chain)

            # Wait for wave to finish transmission
            while self._pi.wave_tx_busy():
                if self._stop:
                    break
                time.sleep(0.1)

    def _angle_to_steps(self, angle):
        """ Convert a number of degrees to the closest number of steps.

        Args:
            angle (float): The number of degrees.

        Returns:
            int: The equivalent number of steps.
        """
        return round(self.FULL_STEPS_PER_TURN * self._microsteps * angle / 360.)

    def _angular_speed_to_step_speed(self, speed):
        """ Convert a speed in degrees/second to steps/second.

        Args:
            speed (float): The speed in degrees/second.

        Returns:
            float: The equivalent speed in steps/second.
        """
        return self.FULL_STEPS_PER_TURN * self._microsteps * speed / 360.

    def _angular_speed_to_step_delay(self, speed):
        """ Convert a speed in degrees/second to the step delay
        (half pulse period).

        Args:
            speed (float): The speed in degrees/second.

        Returns:
            float: The equivalent pulse time in seconds.
        """
        return 1 / (4 * self._angular_speed_to_step_speed(speed))

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
        step_delay = self._angular_speed_to_step_delay(abs(speed))

        self.step(steps, step_delay)

    def move_by_angle_in_time(self, angle, seconds):
        """ Move the motor a number of degrees in a period of time.

        Args:
            angle (float): Number of degrees to move.
            time (float): Time in which to move the motor by degrees.
        """
        self.move_by_angle_at_speed(angle, angle / seconds)

    def move_at_speed_for_time(self, speed, seconds):
        """ Move the motor a number of degrees in a period of time.

        Args:
            speed (float): Speed in degrees/second to move at.
            time (float): Time to move the motor for in seconds.
        """
        self.move_by_angle_at_speed(speed * seconds, speed)



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
                microsteps you have set it to in order for thecontroller
                to operate correctly. The default 1 microstep means the
                motor is taking full steps.

        Raises:
            ValueError: If too many microstep pins are passed.
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
        """ Initialize the GPIO pins. """
        super()._initialize_gpio()

        self._pi.set_mode(self._enable_pin, pigpio.OUTPUT)
        self._pi.write(self._enable_pin, False)

    def _cleanup_gpio(self):
        """ Reset all pins to low to cleanup. """
        super()._cleanup_gpio()

        self._pi.write(self._enable_pin, True)
