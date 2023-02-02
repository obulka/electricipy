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
from dataclasses import dataclass, field
from time import sleep

# Local Imports
from ..signals.pwm import PWMController, PWMSignal


@dataclass
class Servo(PWMSignal):
    """"""

    min_position: float = -90
    max_position: float = 90

    @property
    def position(self):
        """ The servo position, whether this is angualr or linear
        position is up to the user.
        """
        return self.pulse_width_to_position(self.pulse_width)

    @position.setter
    def position(self, new_position):
        self.pulse_width = self.position_to_pulse_width(new_position)

    @property
    def angle(self):
        """ The servo angle, equivalent to the position. """
        return self.position

    @angle.setter
    def angle(self, new_angle):
        self.position = new_angle

    @property
    def mid_position(self):
        """"""
        return self.min_position + (self.max_position - self.min_position) / 2

    def position_to_pulse_width(self, position):
        """"""
        return (
            (self.max_pulse_width - self.min_pulse_width)
            / (self.max_position - self.min_position)
            * (position - self.min_position)
            + self.min_pulse_width
        )

    def pulse_width_to_position(self, pulse_width):
        """"""
        return (
            (self.max_position - self.min_position)
            / (self.max_pulse_width - self.min_pulse_width)
            * (pulse_width - self.min_pulse_width)
            + self.min_position
        )


@dataclass
class SG90(Servo):
    """"""


@dataclass
class HK15148B(Servo):
    """"""
    min_angle: float = -30
    max_angle: float = 30


class ServoController(PWMController):
    """"""

    def go_to(self, position, index=-1):
        """"""
        if index >= 0:
            self[index].position = position
        else:
            for servo in self:
                servo.position = position

        self.update()

    def go_to_positions(self, positions):
        """ Move the servos to the specified positions, whether they be
        angular or linear positions.
        """
        for servo, position in zip(self, positions):
            servo.position = position

        self.update()

    def go_to_position_for_time(self, positions, time):
        """"""
        for servo, position in zip(self, positions):
            servo.servo = position

        with self:
            self.update()
            sleep(time)
