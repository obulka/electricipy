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
# 3rd Party Imports
import pigpio

# Local Imports
from pilectric import GPIOController


class PWM(GPIOController):
    """ This class may be used to generate PWM on multiple GPIO
    at the same time.
    """

    def __init__(self, pins, frequency=1e3, pi_connection=None):
        """ Instantiate the PWM.

        Args:
            pins (list(int,)): The pins to run PWM on.

        Keyword Args:
            frequency (float): The frequency.
            pi_connection (pigpio.pi): The connection to the raspberry
                pi. If not specified, we assume the code is running on a
                pi and use the local gpio.
        """
        super().__init__(pi_connection=pi_connection)

        self._frequency = frequency
        self._period = 1e6 / frequency

        self._pins = {pin: [0., 0.] for pin in pins}

        self._current_wave_id = None

    @property
    def frequency(self):
        """ float: PWM frequency in Hertz. """
        return self._frequency

    @frequency.setter
    def frequency(self, new_frequency):
        self._frequency = float(new_frequency)
        self._period = 1e6 / self._frequency

    @property
    def period(self):
        """ float: PWM period in microseconds. """
        return self._period

    @period.setter
    def period(self, new_period):
        self._period = float(new_period)
        self._frequency = 1e6 / self._period

    def _initialize_gpio(self):
        """ Initialize the GPIO pins. """
        for pin in self._pins:
            self._pi.set_mode(pin, pigpio.OUTPUT)

    def set_pulse_length_in_micros(self, pin, pulse_length):
        """ Sets the GPIO on for pulse_length microseconds per cycle.
        The PWM duty cycle for the GPIO will be
        (pulse_length / period in micros) per cycle.

        The change takes effect when the update function is called.

        Args:
            pin (int): The pin to set the pulse length for.
            pulse_length (float): The pulse length in microseconds.

        Raises:
            ValueError: If the pulse length is longer than the period.
        """
        if pulse_length > self._period:
            raise ValueError(
                f"Invalid pulse length ({pulse_length}us) for period ({self._period}us)"
            )

        if pin not in self._pins:
            self._pins[pin] = [0., 0.]

        self._pins[pin][1] = pulse_length / self._period

    def set_duty_cycle(self, pin, percent):
        """ Sets the GPIO on for length fraction of each cycle. The
        GPIO will be on for (period * percent) microseconds per cycle.

        The change takes affect when the update function is called.

        Args:
            pin (int): The pin to set the duty cycle for.
            percent (float): The percentage of the period that the pulse
                will be high.
        """
        self.set_pulse_length_in_micros(pin, self._period * percent)

    def set_pulse_start_in_micros(self, pin, pulse_start):
        """ Sets the GPIO high at start micros into each cycle.

        The change takes affect when the update function is called.

        Args:
            pin (int): The pin to set the pulse start for.
            pulse_start (float):
                The time into the cycle to begin the pulse.
        """
        if pulse_start > self._period:
            raise ValueError(
                f"Invalid pulse length ({pulse_start}us) for period ({self._period}us)"
            )

        if pin not in self._pins:
            self._pins[pin] = [0., 0.]

        self._pins[pin][0] = pulse_start / self._period

    def set_pulse_start_in_percentage(self, pin, percent):
        """ Sets the GPIO high at a fraction into each cycle.

        The change takes affect when the update function is called.

        Args:
            pin (int): The pin to set the pulse start for.
            percent (float): The percentage of the way into the period
                that the pulse will go high.
        """
        self.set_pulse_start_in_micros(pin, self._period * percent)

    def get_pin_settings(self, pin):
        """ Get the current PWM settings for a GPIO pin.

        Args:
            pin (int): The pin number to get the settings of.

        Returns:
            tuple(float, float):
                The pulse start in microseconds for the given pin, or
                None if the pin is not used. The pulse length in
                microseconds for the given pin, or None if the pin is
                not used.
        """
        return self._pins.get(pin, [None, None])

    def update(self):
        """ Updates the PWM to reflect the current settings. """
        with self:
            for pin, (pulse_start, pulse_length) in self._pins.items():
                on_time = round(pulse_start * self._period)
                length = round(pulse_length * self._period)
                period = round(self._period)

                if length <= 0:
                    self._pi.wave_add_generic([pigpio.pulse(0, 1 << pin, period)])

                elif length >= period:
                    self._pi.wave_add_generic([pigpio.pulse(1 << pin, 0, period)])

                else:
                    off_time = (on_time + length) % period
                    if on_time < off_time:
                        self._pi.wave_add_generic([
                            pigpio.pulse(0, 1 << pin, on_time),
                            pigpio.pulse(1 << pin, 0, off_time - on_time),
                            pigpio.pulse(0, 1 << pin, period - off_time),
                        ])

                    else:
                        self._pi.wave_add_generic([
                            pigpio.pulse(1 << pin, 0, off_time),
                            pigpio.pulse(0, 1 << pin, on_time - off_time),
                            pigpio.pulse(1 << pin, 0, period - on_time),
                        ])

            if self._pins and not self._stop:
                new_wave_id = self._pi.wave_create()

                if self._current_wave_id is not None:
                    self._pi.wave_send_using_mode(
                        new_wave_id,
                        pigpio.WAVE_MODE_REPEAT_SYNC
                    )

                    # Spin until the new wave has started.
                    while self._pi.wave_tx_at() != new_wave_id:
                        pass

                    # It is then safe to delete the old wave.
                    self._pi.wave_delete(self._current_wave_id)

                else:
                    self._pi.wave_send_repeat(new_wave_id)

                self._current_wave_id = new_wave_id

    def stop(self):
        """ Stops the current PWM immediately. """
        super().stop()

        if self._pi:
            self._pi.wave_tx_stop()

        if self._current_wave_id is not None:
            self._pi.wave_delete(self._current_wave_id)
