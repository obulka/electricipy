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
"""
# Standard Imports
from time import sleep

# Local Imports
from electricipy.raspi.signals.pwm import PWMController
from electricipy.raspi.gpio_controller import GPIOManager


class ServoController(PWMController):
    """Base servo controller class"""


class AngularServoController(ServoController):
    """"""
    def __init__(
            self,
            pin,
            min_angle=-90,
            max_angle=90,
            min_pulse_width=500,
            max_pulse_width=2500,
            initial_pulse_width=1500,
            pi_connection=None):
        """"""
        super().__init__(
            pin,
            min_pulse_width=min_pulse_width,
            max_pulse_width=max_pulse_width,
            initial_pulse_width=initial_pulse_width,
            pi_connection=pi_connection,
        )

        self._min_angle = min_angle
        self._max_angle = max_angle

    def angle_to_pulse_width(self, angle):
        """"""
        return (
            (self._max_pulse_width - self._min_pulse_width)
            / (self._max_angle - self._min_angle)
            * (angle - self._min_angle)
            + self._min_pulse_width
        )

    def pulse_width_to_angle(self, pulse_width):
        """"""
        return (
            (self._max_angle - self._min_angle)
            / (self._max_pulse_width - self._min_pulse_width)
            * (pulse_width - self._min_pulse_width)
            + self._min_angle
        )

    @property
    def angle(self):
        """"""
        return self.pulse_width_to_angle(self._pulse_width)

    @angle.setter
    def angle(self, new_angle):
        self._pulse_width = self.angle_to_pulse_width(new_angle)
        self.start()

    @property
    def min_angle(self):
        """"""
        return self._min_angle

    @property
    def max_angle(self):
        """"""
        return self._max_angle

    @property
    def mid_angle(self):
        """"""
        return self._min_angle + (self._max_angle - self._min_angle) / 2

    def run_at_angle_for_time(self, angle, time):
        """"""
        with self:
            self.angle = angle
            sleep(time)


class SG90(AngularServoController):
    """"""

    def __init__(self, pin):
        """"""
        super(SG90, self).__init__(
            pin,
            min_angle=-90,
            max_angle=90,
        )


class HK15148B(AngularServoController):
    """"""

    def __init__(self, pin):
        """"""
        super(HK15148B, self).__init__(
            pin,
            min_angle=-30,
            max_angle=30,
            min_pulse_width=1000,
            max_pulse_width=2000,
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

