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


PWM Module
"""
# Standard Imports
from dataclasses import dataclass, field
from time import sleep

# 3rd Party Imports
import pigpio

# Local Imports
from .. import OutputController


@dataclass
class PWMSignal:
    """"""

    pin: int
    min_pulse_width: float = 500
    max_pulse_width: float = 2500
    _pulse_width: float = 1500

    @property
    def pulse_width(self) -> float:
        return self._pulse_width

    @pulse_width.setter
    def pulse_width(self, new_pulse_width: float) -> None:
        """"""
        self._pulse_width = max(
            min(new_pulse_width, self.max_pulse_width),
            self.min_pulse_width
        )

    @property
    def percentage(self) -> float:
        """ The percentage of the maximum pulse width being run.
        This is in the range [0, 1].
        """
        return (self.max_pulse_width - self.min_pulse_width) / self.min_pulse_width

    @percentage.setter
    def percentage(self, new_percentage: float) -> None:
        self.pulse_width = (
            new_percentage
            * (self.max_pulse_width - self.min_pulse_width)
            + self.min_pulse_width
        )

    def min(self) -> None:
        """"""
        self.pulse_width = self.min_pulse_width

    def max(self) -> None:
        """"""
        self.pulse_width = self.max_pulse_width

    def mid(self) -> None:
        """"""
        self.pulse_width = (
            (self.max_pulse_width - self.min_pulse_width)
            / 2
            + self.min_pulse_width
        )


class PWMController(OutputController):
    """"""

    def __init__(self, pwm_signals, pi_connection=None):
        self._pwm_signals = pwm_signals
        super().__init__(
            (pwm.pin for pwm in self._pwm_signals),
            pi_connection=pi_connection,
        )

    def __getitem__(self, index):
        return self._pwm_signals[index]

    def __len__(self):
        return len(self._pwm_signals)

    def _initialize_gpio(self):
        """ Initialize the GPIO pins. """
        super()._initialize_gpio()

        for pwm_signal in self:
            self._pi.set_servo_pulsewidth(pwm_signal.pin, 0)

    def _cleanup_gpio(self):
        """ Reset all pins to cleanup. """
        super()._cleanup_gpio()

        for pwm_signal in self:
            self._pi.set_servo_pulsewidth(pwm_signal.pin, 0)

    def update(self):
        """"""
        for pwm_signal in self:
            print(f"setting {pwm_signal.pin} {pwm_signal.pulse_width}")
            self._pi.set_servo_pulsewidth(
                pwm_signal.pin,
                pwm_signal.pulse_width,
            )

    def run_at_percentages(self, percentages):
        """"""
        for pwm_signal, percentage in zip(self, percentages):
            pwm_signal.percentage = percentage

        self.update()

    def min(self, index=-1):
        """"""
        if index >= 0:
            self[index].min()
        else:
            for pwm_signal in self:
                pwm_signal.min()

        self.update()

    def max(self, index=-1):
        """"""
        if index >= 0:
            self[index].max()
        else:
            for pwm_signal in self:
                pwm_signal.max()

        self.update()

    def mid(self, index=-1):
        """"""
        if index >= 0:
            self[index].mid()
        else:
            for pwm_signal in self:
                pwm_signal.mid()

        self.update()

    def run_at_pulse_widths_for_time(self, pulse_widths, time):
        """"""
        for pwm_signal, pulse_width in zip(self, pulse_widths):
            pwm_signal.pulse_width = pulse_width

        with self:
            self.update()
            sleep(time)
