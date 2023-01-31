"""
"""
# Standard Imports
import math

# 3rd Party Imports
import pigpio

# Local Imports
from electricipy.raspi.gpio_controller import GPIOManager

from .. import OutputController


class FiniteWaveForm(OutputController):
    """"""

    FULL_LOOP_DENOMINATOR = 256 * 255 + 255


    def __init__(self, pin, num_cycles, pi_connection=None, period=1e-3):
        """ Initialize the controller.

        Args:
            num_cycles (int): Number of full cycles in the waveform.

        Keyword Args:
            pi_connection (pigpio.pi):
                The connection to the raspberry pi. If not specified, we
                assume the code is running on a pi and use the local
                gpio.
            period (float): The period of the wave.

        Raises:
            ValueError:
                If a raspberry pi connection cannot be established.
        """
        super().__init__(pins=(pin,), pi_connection=pi_connection)

        self._period = period
        self._num_cycles = num_cycles

        self._num_full_loops = self._num_cycles // self.FULL_LOOP_DENOMINATOR
        if self._num_full_loops > self.FULL_LOOP_DENOMINATOR:
            raise ValueError("Too many steps for individual waveform.")

        full_loop_remainder = self._num_cycles % self.FULL_LOOP_DENOMINATOR

        self._final_multiple = full_loop_remainder // 256
        self._final_remainder = full_loop_remainder % 256

        self._id = None

    @property
    def period(self):
        return self._period

    @property
    def num_cycles(self):
        return self._num_cycles

    @property
    def pin(self):
        return self._pins[0]

    @property
    def id(self):
        return self._id

    @property
    def time_span(self):
        return self._period * self._num_cycles

    def _initialize_gpio(self):
        """ Initialize the GPIO pins. """
        super()._initialize_gpio()

        self._id = self._id or self._pi.wave_create()

    def _cleanup_gpio(self):
        """ Reset all pins to cleanup. """
        super()._cleanup_gpio()

        if self._id is not None:
            self._pi.wave_delete(self._id)
            self._id = None


class SquareWave(FiniteWaveForm):
    """"""

    def __init__(
            self,
            pin,
            num_cycles,
            period=1e-3,
            pi_connection=None):
        """
        Args:
            num_cycles (int): Number of full cycles in the waveform.

        Keyword Args:
            period (float): The period of the wave.
            pi_connection (pigpio.pi):
                The connection to the raspberry pi. If not specified, we
                assume the code is running on a pi and use the local
                gpio.
        """
        super().__init__(pin, num_cycles, pi_connection=pi_connection, period=period)

        microsecond_pulse_time = round(1e6 * self._period / 2)

        self._wave_pulses = [
            pigpio.pulse(1 << self.pin, 0, microsecond_pulse_time),
            pigpio.pulse(0, 1 << self.pin, microsecond_pulse_time),
        ]

    def _create_wave_chain(self):
        """
        """
        wave_chain = []

        if self._num_full_loops > 0:
            # This is formatted a bit strange because the contents of the following
            # list are a sort of simple programming language, with integers
            # representing for loops, so I have indented them as if they were
            # a language
            wave_chain.extend([
                255, 0,                # Start loop
                    255, 0,            # Start loop
                        self._id,      # Transmit wave
                    255, 1, 255, 255,  # Repeat 255 + 255 * 256 times
                255, 1,                # Repeat as many full loops as necessary
                self._num_full_loops % 256, self._num_full_loops // 256,
            ])
        wave_chain.extend([
            255, 0,                    # Start loop
                self._id,              # Create wave
            255, 1,                    # Repeat for the remaining steps 
            self._final_remainder, self._final_multiple,
        ])

        return wave_chain

    def run(self):
        """"""
        self._pi.wave_chain(self._create_wave_chain())

    def _initialize_gpio(self):
        """ Initialize the GPIO pins. """
        self._pi.wave_add_generic(self._wave_pulses)

        super()._initialize_gpio()


class FiniteWaveFormManager(FiniteWaveForm):
    """"""

    def __init__(self, waves):
        """ Initialize the manager.

        Args:
            controllers (list(GPIOController)):
                The controllers to manage.
        """
        super().__init__(sorted(waves, key=lambda wave: wave.period))

        min_period = self[0].period
        max_period = self[-1].period

        microsecond_pulse_time = round(1e6 * min_period / 2)

        all_pins = 0
        for controller in self:
            all_pins |= 1 << controller.pin

        cycles_in_minimal_wave = [
            math.ceil(max_period / controller.period) for controller in self
        ]

        self._wave_pulses = [
            pigpio.pulse(all_pins, 0, microsecond_pulse_time),
            pigpio.pulse(0, all_pins, microsecond_pulse_time),
        ]

    def _create_wave_chain(self):
        """"""
        # This is formatted a bit strange because the contents of the following
        # list are a sort of simple programming language, with integers
        # representing for loops, so I have indented them as if they were
        # a language
        wave_chain = [
            255, 0,                               # Start loop
                255, 0,                           # Start loop
                    *[wave.id for wave in self],  # Transmit wave
                255, 1, 255, 255,                 # Repeat 255 + 255 * 256 times
            255, 1,                               # Repeat The Maximum remaining times
            self[0]._num_full_loops % 256, self[0]._num_full_loops // 256,
        ]
        wave_chain.extend([
            255, 0,                               # Start loop
                *[wave.id for wave in self],      # Create wave
            255, 1,                               # Repeat for the remaining steps 
            self[0]._final_remainder, self[0]._final_multiple,
        ])

        return wave_chain

    def run(self):
        """"""
        self[0].pi.wave_chain(self._create_wave_chain())
