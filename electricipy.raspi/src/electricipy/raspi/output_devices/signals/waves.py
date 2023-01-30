"""
"""
# 3rd Party Imports
import pigpio

# Local Imports
from electricipy.raspi.gpio_controller import GPIOController


class WaveForm(GPIOController):
    """"""

    def __init__(self, pin, pi_connection=None, wave_id=None):
        """ Initialize the controller.

        Keyword Args:
            pi_connection (pigpio.pi):
                The connection to the raspberry pi. If not specified, we
                assume the code is running on a pi and use the local
                gpio.

        Raises:
            ValueError:
                If a raspberry pi connection cannot be established.
        """
        super().__init__(pi_connection=pi_connection)

        self._pin = pin
        self._id = wave_id

    @property
    def id(self):
        return self._id

    def _initialize_gpio(self):
        """ Initialize the GPIO pins. """
        self._pi.set_mode(self._step_pin, pigpio.OUTPUT)
        self._id = wave_id or self._pi.wave_create()

    def _cleanup_gpio(self):
        """ Reset all pins to cleanup. """
        if self._id is not None:
            self._pi.wave_delete(self._id)
            self._id = None


class SquareWave(WaveForm)
    """"""

    def __init__(
            self,
            pin,
            num_cycles,
            pi_connection=None,
            wave_id=None,
            period=1e-3):
        """

        Args:
            num_cycles (int): Number of full cycles in the waveform.

        Keyword Args:
            period (float): The period of the wave.
        """
        super().__init__(pin, pi_connection=pi_connection)

        microsecond_pulse_time = round(1e6 * period / 2)

        full_loop_denominator = 256 * 255 + 255
        num_full_loops = num_cycles // full_loop_denominator

        if num_full_loops > full_loop_denominator:
            raise ValueError("Too many steps for individual waveform.")

        full_loop_remainder = num_cycles % full_loop_denominator

        final_multiple = full_loop_remainder // 256
        final_remainder = full_loop_remainder % 256

        self._wave_pulses = [
            pigpio.pulse(1 << self._pin, 0, microsecond_pulse_time),
            pigpio.pulse(0, 1 << self._pin, microsecond_pulse_time),
        ]

        self._wave_chain = [
            255, 0,
                255, 0,
                    self._wave_id,
                255, 1,
                255, 255,
            255, 1,
            num_full_loops % 256, num_full_loops // 256,
        ]
        self._wave_chain.extend([
            255, 0,                          # Start loop
                self._wave_id,               # Create wave
            255, 1,                          # loop end
            final_remainder, final_multiple, # repeat step_remainder + 256 * step_multiple
        ])

    def _initialize_gpio(self):
        """ Initialize the GPIO pins. """
        self._pi.wave_add_generic(self._wave_pulses)

        super()._initialize_gpio()

        self._pi.wave_chain(self._wave_chain)
