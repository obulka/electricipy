#!/usr/bin/env python
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
import argparse
import datetime
import sys
import time

from libsonyapi.camera import NotAvailableError

from electricipy.cameras.intervalometer import Intervalometer
from electricipy.cameras.sony import *


__CAMERA_OPTIONS = {
    "sony": SonyCamera,
    "a6000": SonyA6000,
    "a6100": SonyA6100,
    "a6300": SonyA6300,
    "a6400": SonyA6400,
    "a6500": SonyA6500,
    "a6600": SonyA6600,
}


def parse_args(defaults):
    """ Parse the arguments.

    Args:
        defaults (dict): The default parameters.

    Returns:
        argparse.Namespace: The command line arguments.
    """
    parser = argparse.ArgumentParser(description="Shoot a timelapse.")

    parser.add_argument(
        "--iso",
        dest="iso",
        help="The ISO to shoot at.",
        type=int,
    )
    parser.add_argument(
        "--ss",
        dest="shutter_speed",
        help="The shutter speed to use.",
        type=float,
    )
    parser.add_argument(
        "-n",
        dest="num_images",
        help="The number of images to capture.",
        type=int,
    )
    parser.add_argument(
        "--duration",
        dest="duration",
        help=(
            "The duration to image for. "
            "This will be overriden by the 'num_images' parameter if it is specified."
        ),
        type=float,
    )
    parser.add_argument(
        "-d",
        dest="delay",
        default=defaults["delay"],
        help=(
            "The delay to wait between images. "
            f"Default: {defaults['delay']}"
        ),
        type=float,
    )
    parser.add_argument(
        "-c",
        dest="camera",
        help=(
            "The camera type to connect to. "
            f"The options are: {', '.join(__CAMERA_OPTIONS.keys())}"
        ),
        type=str,
    )
    parser.add_argument(
        "--iface",
        dest="network_interface",
        default=defaults["network_interface"],
        help=(
            "The network interface to connect to the camera over. "
            f"Default: {defaults['network_interface']}"
        ),
        type=str,
    )
    parser.add_argument(
        "-v",
        dest="verbose",
        default=False,
        help="Enable verbosity.",
        action="store_true",
    )

    args = parser.parse_args()

    if args.num_images is None and args.duration is None:
        print("One of -n and --duration must be specified.\n")
        print("Use the -h switch to see usage information.")
        sys.exit()

    elif args.camera is None:
        print("Camera (-c) must be specified.\n")
        print("Use the -h switch to see usage information.")
        sys.exit()

    return args


def main():
    """Connect to a camera and take a timelapse."""
    default_options = {
        "delay": 0.5,
        "network_interface": "wlan0",
    }
    args = parse_args(default_options)

    camera_type = __CAMERA_OPTIONS.get(args.camera)

    camera = None

    if issubclass(camera_type, SonyCamera):
        try:
            camera = camera_type(
                shutter_speed=args.shutter_speed,
                iso=args.iso,
                network_interface=args.network_interface,
                retry_attempts=25,
                retry_delay=2,
            )

        except (ConnectionError, NotAvailableError) as err:
            print(err)
            print("\nConnection to camera failed.")
            print("Is it on and searching for a connection?")

    else:
        print(f"Camera ({args.camera}) not found.")

    if camera is not None:
        print("Connection to camera established.")

        if args.num_images is not None:
            intervalometer = Intervalometer(
                camera,
                args.num_images,
                delay=args.delay,
                verbose=args.verbose,
            )

        else:
            intervalometer = Intervalometer.from_duration(
                camera,
                args.duration,
                delay=args.delay,
            )

        print("Intervalometer ready, starting imaging routine.")
        print(
            f"{intervalometer.num_images} images will be captured in about "
            f"{datetime.timedelta(seconds=intervalometer.duration)} seconds."
        )

        try:
            intervalometer.start()

            sleeps = 1
            while intervalometer.running:
                if sleeps % 5 == 0:
                    print(
                        f"{intervalometer.images_captured}/{intervalometer.num_images}"
                        " images captured..."
                    )
                    sleeps = 0

                sleeps += 1
                time.sleep(5)

        except KeyboardInterrupt:
            intervalometer.abort()

            print("\nKeyboard interrupt received, exiting...")

        else:
            print("Imaging completed successfully.")


if __name__ == "__main__":
    main()
