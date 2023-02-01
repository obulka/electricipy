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

    min_angle: float = -90
    max_angle: float = 90

    @property
    def angle(self):
        """"""
        return self.pulse_width_to_angle(self.pulse_width)

    @angle.setter
    def angle(self, new_angle):
        self.pulse_width = self.angle_to_pulse_width(new_angle)

    @property
    def mid_angle(self):
        """"""
        return self.min_angle + (self.max_angle - self.min_angle) / 2

    def angle_to_pulse_width(self, angle):
        """"""
        return (
            (self.max_pulse_width - self.min_pulse_width)
            / (self.max_angle - self.min_angle)
            * (angle - self.min_angle)
            + self.min_pulse_width
        )

    def pulse_width_to_angle(self, pulse_width):
        """"""
        return (
            (self.max_angle - self.min_angle)
            / (self.max_pulse_width - self.min_pulse_width)
            * (pulse_width - self.min_pulse_width)
            + self.min_angle
        )


@dataclass
class SG90(Servo):
    """"""


@dataclass
class HK15148B(Servo):
    """"""
    min_angle: float = -30
    max_angle: float = 30
    min_pulse_width: float = 1000
    max_pulse_width: float = 2000


class ServoController(PWMController):
    """"""

    def go_to_angle(self, index, angle):
        """"""
        self[index].angle = angle
        self.update()

    def go_to_angles(self, angles):
        """"""
        for servo, angle in zip(self, angles):
            servo.angle = angle

        self.update()

    def go_to_angles_for_time(self, angles, time):
        """"""
        for servo, angle in zip(self, angles):
            servo.angle = angle

        with self:
            self.update()
            sleep(time)
