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
import threading
import time


class Intervalometer:
    """ Automate the process of repeatedly taking pictures. """

    def __init__(self, camera, num_images, delay=0.5, verbose=True):
        """Initialize the intervalometer.

        Args:
            camera (electricipy.cameras.Camera): The camera to shoot
                with.
            num_images (int): The number of images to capture.

        Keyword Args:
            delay (float): The time to pause in between images.
            verbose (bool): Enable/disable verbosity.
        """
        self._num_images = num_images
        self._delay = delay
        self._camera = camera
        self._verbose = verbose

        self._images_captured = 0
        self._is_running = False
        self.__process = None

    @classmethod
    def from_duration(cls, camera, duration, delay=0.5, verbose=True):
        """Create an intervalometer that will run for a set amount of
        time.

        Args:
            camera (electricipy.cameras.Camera): The camera to shoot
                with.
            duration (float): The time to shoot for in seconds.

        Keyword Args:
            delay (float): The time to pause in between images.
            verbose (bool): Enable/disable verbosity.
        """
        return cls(
            camera,
            round((duration + delay) / (camera.shutter_speed + delay)),
            delay=delay,
            verbose=verbose,
        )

    @property
    def duration(self):
        """float: The total time in seconds it will take to capture all images."""
        return self._num_images * (self._camera.shutter_speed + self._delay) - self._delay

    @property
    def num_images(self):
        """int: The number of images to take."""
        return self._num_images

    @property
    def images_captured(self):
        """int: The number of images captured so far."""
        return self._images_captured

    @property
    def images_remaining(self):
        """int: The number of images left to capture."""
        return self._num_images - self._images_captured

    @property
    def fps(self):
        """float: The frames per second."""
        return self._num_images / self.duration

    @property
    def running(self):
        """bool: Whether or not the intervalometer is running."""
        return self.__process is not None and self.__process.is_alive()

    def start(self):
        """ Run the image capture routine if its not already running.

        Returns:
            bool: Whether or not a new routine was started.
        """
        if self.running:
            return False

        self.__process = threading.Thread(target=self._run)
        self.__process.daemon = True
        self.__process.start()

        return True

    def _run(self):
        """ Take the pictures."""
        self._images_captured = 0
        while self._images_captured < self._num_images:
            image_path = self._camera.take_picture()

            if self._verbose:
                print(image_path)

            self._images_captured += 1

            if self._images_captured < self._num_images:
                time.sleep(self._delay)

    def abort(self):
        """Cancel the imaging session."""
        if self._is_running:
            self.__process.terminate()
            self.__process.join()
            self.__process = None
