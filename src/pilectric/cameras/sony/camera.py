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
import json
import requests
import socket
import xml.etree.ElementTree as ET

from libsonyapi.camera import Camera


class SonyCamera(Camera):
    """"""

    def __init__(self, network_interface=None):
        """ Create a connection to interface with a camera.


        """
        self._network_interface = network_interface

        super().__init__()

        self.connected = True # Set to False in base class for some reason

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
