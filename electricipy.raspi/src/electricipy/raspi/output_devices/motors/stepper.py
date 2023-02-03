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
from dataclasses import dataclass, field

# Local Imports
from .. import OutputController
from ..signals.waves import FiniteWaveform, PulseWaveController


@dataclass
class StepperMotorDriver:
    """ Class to store the data of a stepper motor.

    Args:
            step_pin (int): The step pin number to use.
            direction_pin (int): The direction pin number to use.
            microstep_pins (list(int)): The pin numbers for the
                microstep settings. (MS2, MS1)
            microsteps (int):
                The number of microsteps to perform. If you have hard
                wired the microstep pins you must pass the number of
                microsteps you have set it to in order for thecontroller
                to operate correctly. The default 1 microstep means the
                motor is taking full steps.
            gear_ratio (float):
                Number of turns of the motor to get one turn of the
                driven output.
            linear (bool):
                True if the stepper motor controls a linear position.
            pitch (float):
                If the output is a lead/ball screw, the pitch can be
                specified in order to support linear 'go to' commands.
                Measured in meters. This will not be used if linear is
                false.
    """
    _MICROSTEPS = {}
    _FULL_STEPS_PER_TURN = None

    step_pin: int
    direction_pin: int
    enable_pin: int
    microstep_pins: list
    microsteps: int
    _microsteps: int = field(init=False, repr=False, default=1)
    gear_ratio: float = 1.
    linear: bool = False
    pitch: float = 1.
    _counterclockwise: bool = field(init=False, repr=False, default=True)

    @property
    def pins(self) -> tuple:
        """"""
        all_pins = (self.step_pin, self.direction_pin, self.enable_pin)
        for pin in self.microstep_pins:
            all_pins += (pin,)

        return all_pins

    @property
    def microstep_pin_values(self) -> tuple:
        """"""
        return self._MICROSTEPS[self.microsteps]

    @property
    def microsteps(self) -> int:
        """ int: The number of microsteps to take. """
        return self._microsteps

    @microsteps.setter
    def microsteps(self, microsteps: int) -> None:
        self._check_microstep_value(microsteps)
        self._microsteps = microsteps

    def _check_microstep_value(self, microsteps: int) -> None:
        """ Check if a number of microsteps is a valid option.

        Raises:
            ValueError: If the number of microsteps is invalid.
        """
        if microsteps not in self._MICROSTEPS:
            raise ValueError(
                f"Invalid number of microsteps: {microsteps}\n"
                f"Valid options are {self._MICROSTEPS.keys()}"
            )

    @property
    def counterclockwise(self) -> bool:
        """ bool: True if motor set to rotate counterclockwise, False if
        clockwise.
        """
        return self._counterclockwise

    @counterclockwise.setter
    def counterclockwise(self, rotate_counterclockwise: bool) -> None:
        self._counterclockwise = rotate_counterclockwise

    @property
    def clockwise(self) -> bool:
        """ bool: True if motor set to rotate clockwise, False if
        counterclockwise.
        """
        return not self._counterclockwise

    @clockwise.setter
    def clockwise(self, rotate_clockwise: float) -> None:
        self._counterclockwise = not rotate_clockwise

    def angle_to_steps(self, angle: float) -> int:
        """ Convert a number of degrees to the closest number of steps.

        Args:
            angle (float): The number of degrees.

        Returns:
            int: The equivalent number of steps.
        """
        return round(
            self.gear_ratio
            * self._FULL_STEPS_PER_TURN
            * self._microsteps
            * angle
            / 360.
        )

    def steps_to_angle(self, steps: int) -> float:
        """ Convert a number of degrees to the closest number of steps.

        Args:
            steps (int): The number of steps.

        Returns:
            float: The equivalent angle.
        """
        return (
            steps * 360
            / self.gear_ratio
            / self._FULL_STEPS_PER_TURN
            / self._microsteps
        )

    def angular_speed_to_step_speed(self, speed: float) -> float:
        """ Convert a speed in degrees/second to steps/second.

        Args:
            speed (float): The speed in degrees/second.

        Returns:
            float: The equivalent speed in steps/second.
        """
        return (
            self.gear_ratio
            * self._FULL_STEPS_PER_TURN
            * self._microsteps
            * speed
            / 360
        )

    def angular_speed_to_step_period(self, speed: float) -> float:
        """ Convert a speed in degrees/second to the step delay
        (pulse period).

        Args:
            speed (float): The speed in degrees/second.

        Returns:
            float: The equivalent pulse time in seconds.
        """
        return 1 / (2 * self.angular_speed_to_step_speed(speed))

    def distance_to_angle(self, distance: float) -> float:
        """ Convert a distance in meters to the angle that the motor
        needs to turn.

        Args:
            distance (float): The distance in meters.

        Returns:
            float: The equivalent angle.
        """
        if not self.linear:
            raise ValueError("The stepper is not linear.")

        return 360. * distance / self.pitch


@dataclass
class TMC2209(StepperMotorDriver):
    """ Control a stepper motor using a TMC2209 v1.2 control board """
    _MICROSTEPS = {
        8: (False, False),
        32: (False, True),
        64: (True, False),
        16: (True, True),
    }
    _FULL_STEPS_PER_TURN = 200

    def _check_microstep_value(self, microsteps: int) -> None:
        """ Check if a number of microsteps is a valid option.

        Raises:
            ValueError: If the number of microsteps is invalid.
        """
        if len(self.microstep_pins) > 2:
            raise ValueError(
                "Too many microstep pins specified, there are only two.",
            )
        super()._check_microstep_value(microsteps)


class StepperMotorController(OutputController):
    """ Base class for control of stepper motors. """

    def __init__(self, stepper_drivers: list, pi_connection=None):
        """ Stepper motor control class.

        Note: Uses BCM mode for compatibility with pigpio.

        Args:
            stepper_drivers (list(StepperMotorDriver)): The stepper
                motors to control.

        Keyword Args:
            pi_connection (pigpio.pi):
                The connection to the raspberry pi. If not specified, we
                assume the code is running on a pi and use the local
                gpio.
        """
        self._stepper_drivers = stepper_drivers

        super().__init__(
            [pin for stepper_driver in self for pin in stepper_driver.pins],
            pi_connection=pi_connection,
        )

        self._wave = None

    def __getitem__(self, index):
        return self._stepper_drivers[index]

    def __len__(self):
        return len(self._stepper_drivers)

    def _initialize_gpio(self):
        """ Initialize the GPIO pins. """
        super()._initialize_gpio()

        for stepper_driver in self:
            self._pi.write(stepper_driver.direction_pin, stepper_driver.counterclockwise)
            self._pi.write(stepper_driver.enable_pin, False)

            for pin, pin_value in zip(
                stepper_driver.microstep_pins,
                stepper_driver.microstep_pin_values
            ):
                self._pi.write(pin, pin_value)

    def _cleanup_gpio(self):
        """ Reset all pins to cleanup. """
        super()._cleanup_gpio()

        for stepper_driver in self:
            self._pi.write(stepper_driver.direction_pin, False)
            self._pi.write(stepper_driver.enable_pin, True)

            for pin in stepper_driver.microstep_pins:
                self._pi.write(pin, False)

    def stop(self):
        """ Stops the current routine immediately. """
        if self._wave:
            self._wave.stop()
        super().stop()

    @property
    def wave(self):
        return self._wave

    def _run(self):
        """ Step the motor through the loaded wave function. """
        with self:
            self._wave.run()

    def prepare_to_move_by_angles_in_time(self, angles, time):
        """ Load the waveform required to move the motor a number of
        degrees in a time.

        Args:
            angles (list(float)): Number of degrees to move.
            time (float): Time in seconds to move through the angle.
        """
        wave_data = []
        for stepper_driver, angle in zip(self, angles):
            if angle < 0:
                stepper_driver.clockwise = True
            else:
                stepper_driver.counterclockwise = True

            steps = stepper_driver.angle_to_steps(abs(angle))

            wave_data.append(FiniteWaveform(stepper_driver.step_pin, steps))

        self._wave = PulseWaveController(wave_data, time, pi_connection=self._pi)

    def prepare_to_move_at_speeds_for_time(self, speeds, time):
        """ Load the waveform required to move the motors a number of
        degrees in a period of time.

        Args:
            speeds (list(float)): Speed in degrees/second to move at.
            time (float): Time to move the motor for in seconds.
        """
        self.prepare_to_move_by_angles_in_time(
            [speed * time for speed in speeds],
            time,
        )

    def prepare_to_move_by_distances_in_time(self, distances, time):
        """ Load the waveform required to move the motor a distance in a
        period of time.

        Args:
            distances (list(float)): Distance in meters to move.
            time (float): Time to move the motor for in seconds.
        """
        angles = []
        for stepper_driver, distance in zip(self, distances):
            if stepper_driver.linear:
                angles.append(stepper_driver.distance_to_angle(distance))
            else:
                angles.append(distance)

        self.prepare_to_move_by_angles_in_time(angles, time)

    def move_by_angles_in_time(self, angles, time):
        """ Move the motors a number of degrees in a period of time.

        Args:
            angles (list(float)): Number of degrees to move.
            time (float): Time in which to move the motor by degrees.
        """
        self.prepare_to_move_by_angles_in_time(angles, time)
        self._run()

    def move_at_speeds_for_time(self, speeds, time):
        """ Move the motors a number of degrees in a period of time.

        Args:
            speeds (list(float)): Speed in degrees/second to move at.
            time (float): Time to move the motor for in seconds.
        """
        self.prepare_to_move_at_speeds_for_time(speeds, time)
        self._run()

    def move_by_distances_in_time(self, distances, time):
        """ Move the motors a distance in a period of time.

        Args:
            distances (list(float)):
                Distance in meters or degrees to move. This will be in
                meters if the stepper is specified as linear, and will
                be in degrees of rotation if not.
            time (float): Time to move the motor for in seconds.
        """
        self.prepare_to_move_by_distances_in_time(distances, time)
        self._run()
