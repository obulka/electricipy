# electricipy

This module allows for easy control over a variety of hardware components.


## Setup

See the module specific README files under electricipy and electricipy.raspi


## Examples

### Connect to Camera

This example connects to a Sony camera and takes a picture. Before running this you must turn on the camera and go to Menu->Application List->Smart Remote Embedded.

```python
from electricipy.cameras.sony import SonyCamera

camera = SonyCamera(network_interface="wlan0")
camera.iso = 400
camera.shutter_speed = 0.1
camera.take_picture()
```

### Intervalometer

This example connects to a camera and takes 10 pictures, with a delay of 1 second in between.

```python
import time

from electricipy.cameras.intervalometer import Intervalometer
from electricipy.cameras.sony import SonyCamera

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

### Timelapse

There is a commandline tool named 'timelapse' that can be used to easily connect to and shoot a timelapse. Run `timelapse -h` to see the usage information. An example use would be `timelapse --iso 100 --ss 1 -c sony -n 10 -v`. Use Ctrl+C to abort the timelapse at any time.


### Stepper Motor Control

This example rotates the motor ccw at 1Hz for 1min, then rotates it cw a quarter turn in 15s, and finally completes a full ccw rotation in 1s. This assumes you are using a TMC2209 stepper motor driver and have it hooked up to the specified pins. Motor control is a work in progress. Note that a negative angle will rotate clockwise, but not a negative speed (it's not velocity!)

```python
from electricipy.raspi.motors import stepper

step_pins = [18, 13]
direction_pins = [3, 27]
enable_pins = [4, 17]
microstep_pins = [[15, 14], [24, 23]]
microsteps = [64, 64]

motor_manager = stepper.TMC2209(
    step_pins,
    direction_pins,
    enable_pins,
    microstep_pins,
    microsteps,
)

motor.move_at_speed_for_time(360, 60)
motor.move_by_angle_in_time(-90, 15)
motor.move_by_angle_at_speed(360, 360)
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
