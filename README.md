# Pilectric

This module aims to create an abstraction layer on top of the raspberry pi GPIO module, allowing for easy control over components such as motors.


## Setup

1. Start the pigpio daemon by running `sudo systemctl enable pigpiod && sudo systemctl start pigpiod` on the raspberry pi.
2. This project's dependencies are managed by pipenv. To enter the virtual environment run:

    `pipenv shell`

    `pipenv install`

## Documentation

The documentation is built using sphinx. To build the documentation run:
    `pipenv install --dev`

    `cd docs`

    `make html`

    `cd build/html`

    `python -m http.server 8000`

To view the documentation go to localhost:8000 in a browser.
