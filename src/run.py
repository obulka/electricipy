#!/usr/bin/env python3
""" Testing
"""
import RPi.GPIO as GPIO
import sys
import time


class StopMotor(Exception):
    """ Stop the motor """
    pass


class Nema17:
    """"""

    def __init__(self, step_pin, direction_pin, verbose=False):
        """ Nema 17 stepper motor control class.

        Note: Uses BOARD mode for compatibility with more Pi versions

        Args:
            step_pin (int): The step pin number to use
            direction_pin (int): The direction pin number to use
        """
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)

        self._step_pin = step_pin
        self._direction_pin = direction_pin

        self._verbose = verbose

        self._stop_motor = False
        self._clockwise = True

    @property
    def clockwise(self):
        return self._clockwise

    @clockwise.setter
    def clockwise(self, rotate_clockwise):
        self._clockwise = rotate_clockwise

    def _initialize_gpio(self):
        """"""
        GPIO.setup(self._step_pin, GPIO.OUT)
        GPIO.setup(self._direction_pin, GPIO.OUT)
        GPIO.output(self._direction_pin, self._clockwise)

    def _cleanup_gpio(self):
        """"""
        GPIO.output(self._step_pin, False)
        GPIO.output(self._direction_pin, False)

    def stop(self):
        """"""
        self._stop_motor = True


class TMC2209(Nema17):
    """"""

    MICROSTEPS = {
        8: (False, False),
        32: (False, True),
        64: (True, False),
        16: (True, True),
    }

    FULL_STEPS_PER_TURN = 200

    def __init__(
            self,
            step_pin,
            direction_pin,
            enable_pin,
            microstep_pins=[],
            verbose=False):
        """"""
        if len(microstep_pins) > 2:
            raise ValueError(
                "Too many microstep pins specified, there are only two."
            )
        super(TMC2209, self).__init__(step_pin, direction_pin, verbose=verbose)

        self._enable_pin = enable_pin
        self._microstep_pins = microstep_pins

        self._microsteps = 64

    @property
    def microsteps(self):
        """int: """
        return self._microsteps

    @microsteps.setter
    def microsteps(self, microsteps):
        """"""
        if microsteps not in self.MICROSTEPS:
            raise ValueError(
                f"Invalid number of microsteps: {microsteps}\n"
                f"Valid options are {self.MICROSTEPS.keys()}"
            )

        self._microsteps = microsteps

    def _initialize_gpio(self):
        super(TMC2209, self)._initialize_gpio()

        GPIO.setup(self._enable_pin, GPIO.OUT)
        GPIO.output(self._enable_pin, False)

        microstep_pin_values = self.MICROSTEPS[self._microsteps]
        for pin, pin_value in zip(self._microstep_pins, microstep_pin_values):
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, pin_value)

    def _cleanup_gpio(self):
        super(TMC2209, self)._cleanup_gpio()

        GPIO.output(self._enable_pin, True)

        for pin in self._microstep_pins:
            GPIO.output(pin, False)

    def step_motor(self, num_steps, step_delay=.005):
        """"""
        self._stop_motor = False

        self._initialize_gpio()

        try:
            for step in range(num_steps):
                # if self._stop_motor:
                #     raise StopMotor
                # else:
                GPIO.output(self._step_pin, True)
                time.sleep(step_delay)

                GPIO.output(self._step_pin, False)
                time.sleep(step_delay)

                # if self._verbose:
                #     print(f"Step count {step + 1}", end="\r", flush=True)

            if self._verbose:
                print("Motor has moved:")
                print(f"Number of steps: {num_steps}")
                print(f"Step Delay = {step_delay}")
                print(f"Clockwise = {self._clockwise}")
                print(f"Microsteps = {self._microsteps}")

        finally:
            print("Cleaning Up")
            self._cleanup_gpio()

    def _degrees_to_steps(self, degrees):
        return round(self.FULL_STEPS_PER_TURN * self._microsteps * degrees / 360.)

    def _speed_to_step_delay(self, speed):
        """
        """
        return 180. / (self.FULL_STEPS_PER_TURN * self._microsteps * speed)

    def move_motor_at_speed(self, degrees, speed):
        """ Move the motor.

        Args:
            degrees (float): Number of degrees to move
            speed (float): Speed in degrees/second to move at
        """
        steps = self._degrees_to_steps(degrees)
        step_delay = self._speed_to_step_delay(speed)

        self.step_motor(steps, step_delay)

    def move_motor_in_time(self, degrees, seconds):
        """ Move the motor.

        Args:
            degrees (float): Number of degrees to move
            speed (float): Speed in degrees/second to move at
        """
        self.move_motor_at_speed(degrees, degrees / seconds)


def main():
    print("hello")

    num_full_steps_per_cycle = 200
    step_pin = 3
    direction_pin = 5
    enable_pin = 7
    microstep_pins = [10, 8]

    motor = TMC2209(
        step_pin,
        direction_pin,
        enable_pin,
        microstep_pins=microstep_pins,
        verbose=False,
    )

    time.sleep(0.5)

    for step_cycle in range(3): 
        motor.move_motor_in_time(180., 1.)
        time.sleep(1)


if __name__ == "__main__":
    main()
