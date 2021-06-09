""" PWM Module """
import pigpio


class PWM:
    """ This class may be used to generate PWM on multiple GPIO
    at the same time.

    The following diagram illustrates PWM for one GPIO.

    1      +------------+             +------------+
             |    GPIO    |             |    GPIO    |
             |<--- on --->|             |<--- on --->|
             |    time    |             |    time    |
    0 -----+            +-------------+            +---------
          on^         off^           on^         off^
      +--------------------------+--------------------------+
      ^                          ^                          ^
      |<------ cycle time ------>|<------ cycle time ------>|
    cycle                      cycle                      cycle
    start                      start                      start

    The underlying PWM frequency is the same for all GPIO and
    is the number of cycles per second (known as Hertz).

    The frequency may be specified in Hertz or by specifying
    the cycle time in microseconds (in which case a frequency
    of 1000000 / cycle time is set).

    The PWM duty cycle (the proportion of on time to cycle time)
    and the start of the on time within each cycle may be set on
    a GPIO by GPIO basis.

    The GPIO PWM duty cycle may be set as a fraction of the
    cycle time (0-1.0) or as the on time in microseconds.
    """

    def __init__(self, pins, frequency=1000, pi_connection=None):
        """ Instantiate the PWM.

        Args:
            frequency (float): The frequency.
            pins (tuple(int,)): The pins to run PWM on.

        Keyword Args:
            pi_connection ():
        """
        self._pi = pi_connection if pi_connection else pigpio.pi()
        if not self._pi.connected:
            raise ValueError("Unable to connect to a raspberry pi")
        self.__internal_pi_connection = pi_connection is None

        self._frequency = frequency
        self._period = 1000000 / frequency

        self._pins = {pin: (0., 0.) for pin in pins}

        self._current_wave_id = None
        self._stop = False

    def __del__(self):
        """ Cleanup """
        self.stop()
        if self.__internal_pi_connection:
            self._pi.stop()

    @property
    def frequency(self):
        """ float: PWM frequency in Hertz. """
        return self._frequency

    @frequency.setter
    def frequency(self, new_frequency):
        self._frequency = float(new_frequency)
        self._period = 1000000 / self._frequency

    @property
    def period(self):
        """ float: PWM period in microseconds. """
        return self._period

    @period.setter
    def period(self, new_period):
        self._period = float(new_period)
        self._frequency = 1000000 / self._period

    def _initialize_gpio(self):
        """ Initialize the GPIO pins. """
        for pin in self._pins:
            self._pi.set_mode(pin, pigpio.OUTPUT)

    def set_pulse_length_in_micros(self, pin, pulse_length):
        """ Sets the GPIO on for length microseconds per cycle.

        The PWM duty cycle for the GPIO will be:

        (length / cycle length in micros) per cycle

        The change takes affect when the update function is called.
        """
        if pulse_length > self._period:
            raise ValueError(
                f"Invalid pulse length ({pulse_length}us) for period ({self._period}us)"
            )

        if pin not in self._pins:
            self._pins[pin] = (0., 0.)

        self._pins[pin][1] = pulse_length / self._period

    def set_pulse_length_in_percentage(self, pin, percent):
        """ Sets the GPIO on for length fraction of each cycle.

        The GPIO will be on for:

        (cycle length in micros * length) microseconds per cycle

        The change takes affect when the update function is called.
        """
        self.set_pulse_length_in_micros(pin, self._period * percent)

    def set_pulse_start_in_micros(self, pin, pulse_start):
        """ Sets the GPIO high at start micros into each cycle.

        The change takes affect when the update function is called.
        """
        if pulse_start > self._period:
            raise ValueError(
                f"Invalid pulse length ({pulse_start}us) for period ({self._period}us)"
            )

        if pin not in self._pins:
            self._pins[pin] = (0., 0.)

        self._pins[pin][0] = pulse_start / self._period

    def set_pulse_start_in_percentage(self, pin, percent):
        """ Sets the GPIO high at start fraction into each cycle.

        The change takes affect when the update function is called.
        """
        self.set_pulse_start_in_micros(pin, self._period * percent)

    def get_pin_settings(self, pin):
        """ Get the current PWM settings for a GPIO pin.

        Args:
            pin (int): The pin number to get the settings of.

        Returns:
            float:
                The pulse start in microseconds for the given pin,
                or None if the pin is not used.
            float:
                The pulse length in microseconds for the given pin,
                or None if the pin is not used.
        """
        return self._pins.get(pin, (None, None))

    def update(self):
        """ Updates the PWM to reflect the current settings. """
        self._initialize_gpio()

        for pin, (pulse_start, pulse_length) in self._pins:
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
        """
        Cancels PWM on the GPIO.
        """
        self._stop = True

        self._pi.wave_tx_stop()

        if self._current_wave_id is not None:
            self._pi.wave_delete(self._current_wave_id)
