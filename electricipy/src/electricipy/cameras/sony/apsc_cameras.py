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
from .camera import SonyCamera
from ..sensors import APSC


class SonyAPSCCamera(SonyCamera):
    """ Class to control a Sony camera """

    def __init__(
            self,
            shutter_speed=None,
            iso=None,
            network_interface=None,
            disable_auto_iso=True,
            retry_attempts=1,
            retry_delay=1):
        """ Create a connection to interface with a sony camera.

        Keyword Args:
            shutter_speed (float): The shutter speed in seconds.
            iso (int): The initial ISO.
            network_interface (str): The network interface to use when
                connecting to the camera.
            disable_auto_iso (bool): If True the ISO will be
                automatically set, disabling AUTO.
            retry_attempts (int): The number of times to retry
                connecting.
            retry_delay (float): The delay between retry attempts.

        Raises:
            requests.exceptions.ConnectionError: If the camera cannot be
                connected to.
            libsonyapi.camera.NotAvailableError: If the camera is not
                available.
        """
        super().__init__(
            shutter_speed=shutter_speed,
            iso=iso,
            network_interface=network_interface,
            sensor=APSC(),
            disable_auto_iso=disable_auto_iso,
            retry_attempts=retry_attempts,
            retry_delay=retry_delay,
        )


class SonyA6000(SonyAPSCCamera):
    """"""


class SonyA6100(SonyAPSCCamera):
    """"""


class SonyA6300(SonyAPSCCamera):
    """"""


class SonyA6400(SonyAPSCCamera):
    """"""


class SonyA6500(SonyAPSCCamera):
    """"""


class SonyA6600(SonyAPSCCamera):
    """"""
