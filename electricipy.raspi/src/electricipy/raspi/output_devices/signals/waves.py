"""
"""
# Standard Imports
from dataclasses import dataclass
import math

# 3rd Party Imports
import pigpio

# Local Imports
from .. import OutputController


@dataclass
class FiniteWaveform:
    """ Data needed to create a waveform with a fixed number of cycles.

    Args:
        num_cycles (int): Number of full cycles in the waveform.

    Keyword Args:
        period (float): The period of the wave.
    """
    pin: int
    num_cycles: int
    period: float = 1e-3

    @property
    def time_span(self):
        return self.period * self.num_cycles

    @property
    def frequency(self):
        """"""
        return 1 / self.period


class PulseWaveController(OutputController):
    """"""

    _FULL_LOOP_DENOMINATOR = 256 * 255 + 255
    MAX_PULSES_PER_SOCKET_MESSAGE = 5461


    def __init__(self, waves, time, pi_connection=None):
        """ Initialize the controller. This controller guarantees the
        correct number of cycles occur in each wave, even if the time
        cannot be precisely guaranteed. The waves periods will be
        overridden in order to conform with the time arg.

        Args:
            waves (list(FiniteWaveform)): The waves to control.
            time (float): The amount of time to synchronously complete
                the waves.

        Keyword Args:
            pi_connection (pigpio.pi):
                The connection to the raspberry pi. If not specified, we
                assume the code is running on a pi and use the local
                gpio.
        Raises:
            ValueError:
                If a raspberry pi connection cannot be established,
                the wave exceeds the maximum cycles (4294901760), or no
                waves are provided.
        """
        if not waves:
            raise ValueError("At least one wave must be provided.")

        super().__init__(
            [wave.pin for wave in waves],
            pi_connection=pi_connection
        )

        self._ids = []

        self._wave_pulses = []
        self._num_full_loops = 0
        self._final_multiple = 0
        self._final_remainder = 0

        for wave in waves:
            wave.period = time / wave.num_cycles

        self.waves = waves

    def __getitem__(self, index):
        return self._waves[index]

    def __len__(self):
        return len(self._waves)

    def add_wave(wave):
        """ Add a new wave to be controlled.

        Args:
            wave (FiniteWaveform): The wave to control.
        """
        self.waves = self._waves + [wave]

    @property
    def waves(self):
        """  list(FiniteWaveform): The waves being controlled in order
        from shortest to longest period.
        """
        return self._waves

    @waves.setter
    def waves(self, new_waves):
        if not new_waves:
            raise ValueError("At least one wave must be provided.")

        self._waves = sorted(new_waves, key=lambda wave: wave.period)
        self._pins = [wave.pin for wave in self]

        self._update_waveform()

    @property
    def min_period(self):
        """"""
        return self[0].period

    @property
    def max_period(self):
        """"""
        return self[-1].period

    @property
    def min_cycles(self):
        """"""
        return self[-1].num_cycles

    @property
    def max_cycles(self):
        """"""
        return self[0].num_cycles

    def _initialize_gpio(self):
        """ Initialize the GPIO pins. """
        super()._initialize_gpio()

        try:
            # There is a limit to the number of pulses that can be sent over
            # the socket at a time, so we must break large amounts of wave
            # pulses up into smaller chunks, and even then if we don't split
            # it into multiple waves, only the final message will be used.
            range_start = 0
            range_end = self.MAX_PULSES_PER_SOCKET_MESSAGE
            for _ in range(len(self._wave_pulses) // self.MAX_PULSES_PER_SOCKET_MESSAGE):
                self._pi.wave_add_generic(self._wave_pulses[range_start:range_end])
                self._ids.append(self._pi.wave_create())

                range_start = range_end
                range_end += self.MAX_PULSES_PER_SOCKET_MESSAGE

            # Add the remainder of the pulses
            self._pi.wave_add_generic(self._wave_pulses[range_start:])

            self._ids.append(self._pi.wave_create())

        except pigpio.error:
            self._cleanup_gpio()
            raise

    def _cleanup_gpio(self):
        """ Reset all pins to cleanup. """
        super()._cleanup_gpio()

        self._pi.wave_clear()

        self._ids = []

    @staticmethod
    def split_waveforms(waveforms):
        """"""
        max_allowed_cycles_per_waveform = PulseWaveController.MAX_PULSES_PER_SOCKET_MESSAGE // 2
        print(f"max_allowed_cycles_per_waveform {max_allowed_cycles_per_waveform}")
        max_cycles_in_movement = max([wave.num_cycles for wave in waveforms])
        print(f"max_cycles_in_movement {max_cycles_in_movement}")

        num_splits = max_cycles_in_movement // max_allowed_cycles_per_waveform
        print(f"num_splits {num_splits}")

        split_waveforms = []
        for split_num in range(num_splits):
            split_waveform = []
            for waveform in waveforms:
                cycles = waveform.num_cycles // num_splits
                print(f"had {waveform.num_cycles}")
                split_waveform.append(FiniteWaveform(waveform.pin, cycles))
                print(f"adding cycles {cycles} on {waveform.pin}")

            split_waveforms.append(split_waveform)

        remaining_waveform = []
        for waveform in waveforms:
            cycles = waveform.num_cycles % num_splits
            if cycles > 0:
                remaining_waveform.append(FiniteWaveform(waveform.pin, cycles))
                print(f"adding cycles {cycles} on {waveform.pin}")

        split_waveforms.append(remaining_waveform)

        return split_waveforms

    @staticmethod
    def __greatest_common_divisor(number_generator):
        """"""
        gcd = next(number_generator)
        for number in number_generator:
            gcd = math.gcd(gcd, number)

        return gcd

    def _update_waveform(self):
        """"""
        microsecond_pulse_time = max(1, round(1e6 * self.min_period / 2))

        pulse_cycles = self.__greatest_common_divisor(wave.num_cycles for wave in self)

        self._num_full_loops = pulse_cycles // self._FULL_LOOP_DENOMINATOR
        if self._num_full_loops > self._FULL_LOOP_DENOMINATOR:
            raise ValueError(
                f"Too many pulse cycles for individual waveform: {pulse_cycles}"
                f"/{self._FULL_LOOP_DENOMINATOR**2 + self._FULL_LOOP_DENOMINATOR}"
            )

        full_loop_remainder = pulse_cycles % self._FULL_LOOP_DENOMINATOR

        self._final_multiple = full_loop_remainder // 256
        self._final_remainder = full_loop_remainder % 256

        half_cycles = self.max_cycles * 2 // pulse_cycles

        self._wave_pulses = []
        for half_cycle in range(half_cycles):
            pulse_on = 0
            pulse_off = 0
            for wave in self:
                binary_pin = 1 << wave.pin
                pulse_contribution = (
                    binary_pin
                    * (
                        half_cycle
                        % (half_cycles // (wave.num_cycles // pulse_cycles))
                        == 0
                    )
                )

                pulse_on |= pulse_contribution
                pulse_off |= binary_pin * (pulse_contribution == 0)

            self._wave_pulses.append(
                pigpio.pulse(pulse_on, pulse_off, microsecond_pulse_time),
            )

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
                        *self._ids,    # Transmit waves
                    255, 1, 255, 255,  # Repeat 255 + 255 * 256 times
                255, 1,                # Repeat as many full loops as necessary
                self._num_full_loops % 256, self._num_full_loops // 256,
            ])
        wave_chain.extend([
            255, 0,                    # Start loop
                *self._ids,            # Transmit waves
            255, 1,                    # Repeat for the remaining cycles 
            self._final_remainder, self._final_multiple,
        ])

        return wave_chain

    def run(self):
        """"""
        self._pi.wave_chain(self._create_wave_chain())
