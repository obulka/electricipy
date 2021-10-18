# Pilectric

This module allows for easy control over a variety of hardware components through a Raspberry Pi.


## Setup

1. Start the pigpio daemon by running `sudo systemctl enable pigpiod && sudo systemctl start pigpiod` on the raspberry pi.
2. This project's dependencies are managed by pipenv. To enter the virtual environment run:

    `pipenv shell`

    `pipenv install`

## Examples

### Connect to Camera

This example connects to a Sony camera and takes a picture. Before running this you must turn on the camera and go to Menu->Application List->Smart Remote Embedded.

```python
from libsonyapi import Actions
from pilectric.cameras.sony import SonyCamera

camera = SonyCamera(network_interface="wlan0")
camera.iso = 400
camera.shutter_speed = 0.1
camera.take_picture()
```

## Documentation

The documentation is built using sphinx. To build the documentation run:
    `pipenv install --dev`

    `cd docs`

    `make html`

    `cd build/html`

    `python -m http.server 8000`

To view the documentation go to localhost:8000 in a browser.
