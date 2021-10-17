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
import math


class Camera:
    """ Class to interface with cameras. """

    def __init__(
            self,
            shutter_speed,
            gain,
            sensor=None,
            zero_gain_iso=100,
            decibles_per_stop=20 * math.log10(2)):
        """ Initialize a camera.

        Args:
            shutter_speed (float): The shutter speed in seconds.
            gain (float): The gain in decibles.

        Keyword Args:
            sensor (pilectric.cameras.sensors.sensor.Sensor): The camera
                sensor.
            zero_gain_iso (int): The ISO for which the gain is zero.
            decibles_per_stop (float): The number of decibles it takes
                to double the ISO.
        """
        self._shutter_speed = shutter_speed
        self._gain = gain
        self._sensor = sensor
        self._zero_gain_iso = zero_gain_iso
        self._decibles_per_stop = decibles_per_stop

    @staticmethod
    def gain_to_iso(gain, zero_gain_iso=100, decibles_per_stop=20 * math.log10(2)):
        """ Convert gain to ISO.

        Args:
            gain (float): The gain to convert.

        Keyword Args:
            zero_gain_iso (int): The ISO for which the gain is zero.
            decibles_per_stop (float): The number of decibles it takes
                to double the ISO.

        Returns:
            int: The equivalent ISO.
        """
        return int(zero_gain_iso * 2**(gain / decibles_per_stop))

    @staticmethod
    def iso_to_gain(iso, zero_gain_iso=100, decibles_per_stop=20 * math.log10(2)):
        """ Convert ISO to gain.

        Args:
            iso (int): The ISO to convert.

        Keyword Args:
            zero_gain_iso (int): The ISO for which the gain is zero.
            decibles_per_stop (float): The number of decibles it takes
                to double the ISO.

        Returns:
            float: The equivalent gain.
        """
        return decibles_per_stop * math.log(iso / zero_gain_iso, 2)

    @property
    def shutter_speed(self):
        """float: The camera's shutter speed in seconds."""
        return self._shutter_speed

    @property
    def gain(self):
        """float: The camera's gain in decibles. """
        return self._gain

    @property
    def iso(self):
        """int: The camera's iso. """
        return self.gain_to_iso(
            self._gain,
            zero_gain_iso=self._zero_gain_iso,
            decibles_per_stop=self._decibles_per_stop,
        )

    @iso.setter
    def iso(self, new_iso):
        """ Set the iso.

        Raises:
            ValueError: If the new iso is <= 0.
        """
        self._gain = self.iso_to_gain(
            new_iso,
            zero_gain_iso=self._zero_gain_iso,
            decibles_per_stop=self._decibles_per_stop,
        )

    @property
    def sensor(self):
        """pilectric.cameras.sensors.sensor.Sensor: The camera's sensor"""
        return self._sensor
