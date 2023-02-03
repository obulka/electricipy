# electricipy

This module allows for easy control over a variety of hardware components.


## Setup

See the module specific README files under electricipy and electricipy.raspi


## Examples

### Connect to Camera

This example connects to a Sony camera and takes a picture. Before running this you must turn on the camera and go to Menu->Application List->Smart Remote Embedded. When initializing the camera object you can pass retry_attempts and retry delay parameters to increase the chances of connecting on the first execution.

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

There is a command line tool named 'timelapse' that can be used to easily connect to and shoot a timelapse. Run `timelapse -h` to see the usage information. An example use would be `timelapse --iso 100 --ss 1 -c sony -n 10 -v`. Use Ctrl+C to abort the timelapse at any time.


### Stepper Motor Control

This example rotates the motor ccw at 1Hz for 1min, then rotates it cw a quarter turn in 15s, and finally completes a full ccw rotation in 1s. This assumes you are using a TMC2209 stepper motor driver and have it hooked up to the specified pins. Note that a negative angle will rotate clockwise, but not a negative speed (it's not velocity!) Motor control is a work in progress.

```python
from electricipy.raspi.output_devices.motors import stepper


motor_controller = stepper.StepperMotorController([
    stepper.TMC2209(
        step_pin=18,
        direction_pin=3,
        enable_pin=4,
        microstep_pins=(15, 14),
        microsteps=64,
        gear_ratio=1.,
        linear=True,
        pitch=5e-3,
    ),
    stepper.TMC2209(
        step_pin=13,
        direction_pin=27,
        enable_pin=17,
        microstep_pins=(24, 23),
        microsteps=64,
        gear_ratio=1.,
        linear=False,
    ),
])

motor_controller.move_by_angles_in_time([-720, 360], 2)
motor_controller.move_by_angles_in_time([720, -360], 2)
```

### Servo control

```python
import time

from electricipy.raspi.output_devices.motors.servo import SG90


servo_controller = servo.ServoController([
    servo.HK15148B(
        19,
        max_pulse_width=1225, # My servos don't like large pulse widths
    ),
    servo.SG90(
        20,
        max_pulse_width=1300,
    ),
])

with servo_controller:
    servo_controller.go_to_positions([10, -10])
    time.sleep(5)
    servo_controller.go_to_positions([-10, 10])
    time.sleep(5)
    servo_controller.go_to_positions([20, -20])
    time.sleep(2)
    servo_controller.max()
    time.sleep(2)
    servo_controller.min()
    time.sleep(2)
    servo_controller.mid(0)
    time.sleep(2)
```

### Electronic Speed Controller Driving Brushless Motors

```python
import time

from electricipy.raspi.output_devices.motors import brushless


esc_pin = 19
esc = brushless.ElectronicSpeedController(esc_pin)
with esc:
    esc.initialise()
    esc.mid()
    time.sleep(1)
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
