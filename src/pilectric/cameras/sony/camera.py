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
from fractions import Fraction
import json
import requests
import socket

from libsonyapi.actions import Actions
from libsonyapi.camera import Camera as SonyCameraAPI

from ..camera import Camera


class SonyCamera(SonyCameraAPI, Camera):
    """"""

    def __init__(self, network_interface=None, sensor=None, disable_auto_iso=True):
        """ Create a connection to interface with a camera.
        """
        self._network_interface = network_interface

        SonyCameraAPI.__init__(self)
        self.connected = True # Set to False in base class for some reason

        self._disable_auto_iso = disable_auto_iso

        Camera.__init__(
            self,
            self.shutter_speed,
            self.iso_to_gain(self.iso),
            sensor=sensor,
        )

    @property
    def iso(self):
        """int: The camera's iso. """
        iso = self.run_command(Actions.getIsoSpeedRate)
        if iso == "AUTO":
            self.run_command(Actions.actHalfPressShutter)
            iso = self.run_command(Actions.getIsoSpeedRate)
            self.run_command(Actions.cancelHalfPressShutter)

            if self._disable_auto_iso:
                self.run_command(Actions.setIsoSpeedRate, iso)

        return int(iso)

    @iso.setter
    def iso(self, new_iso):
        if self.run_command(Actions.setIsoSpeedRate, str(new_iso)) == 0:
            if new_iso == "AUTO":
                self.run_command(Actions.actHalfPressShutter)
                new_iso = self.run_command(Actions.getIsoSpeedRate)
                self.run_command(Actions.cancelHalfPressShutter)

                if self._disable_auto_iso:
                    self.run_command(Actions.setIsoSpeedRate, new_iso)

            self._gain = self.iso_to_gain(int(new_iso))

    @property
    def shutter_speed(self):
        """float: The camera's shutter speed in seconds."""
        shutter_speed = self.run_command(Actions.getShutterSpeed)
        if shutter_speed == "BULB":
            return shutter_speed

        self._shutter_speed = float(Fraction(shutter_speed.replace('"', "/1")))

        return self._shutter_speed

    @shutter_speed.setter
    def shutter_speed(self, new_shutter_speed):
        if type(new_shutter_speed) == str:
            new_shutter_speed = new_shutter_speed.strip('"')

        elif type(new_shutter_speed) == float and new_shutter_speed < 1:
            new_shutter_speed = Fraction(new_shutter_speed).limit_denominator()

        if self.run_command(Actions.setShutterSpeed, str(new_shutter_speed)) == 0:
            self._shutter_speed = float(Fraction(new_shutter_speed))

    def discover(self):
        """ Discover camera.

        Raises:
            ConnectionError: If the camera cannot be discovered, usually
                because you are not connected to the camera's wifi.

        Returns:
            str: The XML URL of the camera.
        """
        msg = (
            "M-SEARCH * HTTP/1.1\r\n"
            "HOST: 239.255.255.250:1900\r\n"
            'MAN: "ssdp:discover" \r\n'
            "MX: 2\r\n"
            "ST: urn:schemas-sony-com:service:ScalarWebAPI:1\r\n"
            "\r\n"
        ).encode()

        # Set up UDP socket
        if not hasattr(socket, 'SO_BINDTODEVICE'):
            socket.SO_BINDTODEVICE = 25

        socket_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        if self._network_interface is not None:
            socket_.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_BINDTODEVICE,
                self._network_interface.encode(),
            )
        socket_.settimeout(2)
        socket_.sendto(msg, ("239.255.255.250", 1900))

        try:
            while True:
                data, addr = socket_.recvfrom(65507)
                decoded_data = data.decode()
                # get xml url from ssdp response
                for item in decoded_data.split("\n"):
                    if "LOCATION" in item:
                        return item.strip().split(" ")[1]

        except socket.timeout:
            raise ConnectionError("You are not connected to the camera's wifi.")

    def post_request(self, url, method, param=[]):
        """
        """
        if type(param) is not list:
            param = [param]
        json_request = {"method": method, "params": param, "id": 1, "version": "1.0"}
        request = requests.post(url, json.dumps(json_request))
        response = json.loads(request.content)

        return response

    def run_command(self, command, param=[]):
        """"""
        response = self.do(command, param=param)

        if "error" in response:
            error = response["error"]
            error_code = error[0]
            error_message = error[-1]

            if error_code == 1:
                raise NotAvailableError(error_message)

            elif error_code == 3:
                raise IllegalArgumentError(error_message + ": {}".format(param))

            elif error_code == 12:
                raise InvalidActionError("Invalid action: " + error_message)

            elif error_code == 403:
                raise ForbiddenError(error_message)

            elif error_code == 500:
                raise OperationFailedError(error_message)

            else:
                raise ValueError("Unknown error: " + error_message)

        else:
            result = response.get("result", [])
            if len(result) == 0:
                return True

            elif len(result) == 1:
                return result[0]

            else:
                return result


class NotAvailableError(Exception):
    pass


class IllegalArgumentError(Exception):
    pass


class InvalidActionError(Exception):
    pass


class ForbiddenError(Exception):
    pass


class OperationFailedError(Exception):
    pass
