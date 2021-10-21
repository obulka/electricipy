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
from dataclasses import dataclass, field


@dataclass
class Sensor:
    """ Class to represent a sensor. """
    _sensor_height: float = field(init=False) # millimeters
    _sensor_width: float = field(init=False) # millimeters

    @property
    def sensor_height(self):
        """float: The height of the sensor in millimeters."""
        return self._sensor_height

    @property
    def sensor_width(self):
        """float: The width of the sensor in millimeters."""
        return self._sensor_width


@dataclass
class APSC(Sensor):
    """ Class to represent a full frame sensor. """

    def __post_init__(self):
        self._sensor_height = 15.6
        self._sensor_width = 23.6


@dataclass
class APSH(Sensor):
    """ Class to represent a full frame sensor. """

    def __post_init__(self):
        self._sensor_height = 18.6
        self._sensor_width = 27.9


@dataclass
class CanonAPSC(Sensor):
    """ Class to represent a full frame sensor. """

    def __post_init__(self):
        self._sensor_height = 14.8
        self._sensor_width = 22.2


@dataclass
class FullFrame(Sensor):
    """ Class to represent a full frame sensor. """

    def __post_init__(self):
        self._sensor_height = 24.
        self._sensor_width = 36.


@dataclass
class MicroFourThirds(Sensor):
    """ Class to represent a full frame sensor. """

    def __post_init__(self):
        self._sensor_height = 13.
        self._sensor_width = 17.3
