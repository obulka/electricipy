# electricipy

This module allows for easy control over a variety of hardware components.


## Setup

1. Start the pigpio daemon by running `sudo systemctl enable pigpiod && sudo systemctl start pigpiod` on the raspberry pi.
2. This project's dependencies are managed by pipenv. If you just want to run the project, run: `pipenv install`

4. For development, enter the virtual environment by running: `pipenv shell`

4. If it is your first time in the virtual environment run: `pipenv sync --dev`

## Examples

### Connect to Camera

This example connects to a Sony camera and takes a picture. Before running this you must turn on the camera and go to Menu->Application List->Smart Remote Embedded.

```python
from libsonyapi import Actions
from electricipy.core.cameras.sony import SonyCamera

camera = SonyCamera(network_interface="wlan0")
camera.iso = 400
camera.shutter_speed = 0.1
camera.take_picture()
```

### Intervalometer

This example connects to a camera and takes 10 pictures, with a delay of 1 second in between.

```python
import time

from libsonyapi import Actions

from electricipy.core.cameras.intervalometer import Intervalometer
from electricipy.core.cameras.sony import SonyCamera

camera = SonyCamera(
    shutter_speed=1,
    iso=400,
    network_interface="wlan0",
)

intervalometer = Intervalometer(camera, 10, delay=1)
intervalometer.start()

while intervalometer.running:
    print("Still running...")
    time.sleep(5)
```

## Documentation

The documentation is built using sphinx. To build the documentation run:
```
cd docs
make html
cd build/html
python -m http.server [--bind <ip address>] 8000
```

To view the documentation go to \<ip address\>:8000 in a browser.
