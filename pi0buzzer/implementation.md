
# `pi0buzzer` Implementation Instructions

This document provides a step-by-step guide on how to create the `pi0buzzer` driver.

## 1. Create the project directory

```bash
mkdir -p pi0buzzer/src/pi0buzzer
```

## 2. Create the `pyproject.toml` file

This file defines the project's metadata, dependencies, and entry points.

**File:** `pi0buzzer/pyproject.toml`

```toml
[project]
name = "pi0buzzer"
version = "0.1.0"
description = "A simple buzzer driver for Raspberry Pi."
readme = "README.md"
authors = [{ name = "Gemini", email = "gemini@google.com" }]
requires-python = ">=3.11"
dependencies = [
    "pigpio",
    "click",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project.scripts]
pi0buzzer = "pi0buzzer.__main__:cli"
```

## 3. Create the main driver file

This file contains the `Buzzer` class, which encapsulates the logic for controlling the buzzer.

**File:** `pi0buzzer/src/pi0buzzer/driver.py`

```python
import pigpio
import time
import json
import os
import sys
import tty
import termios
import select

class Buzzer:
    def __init__(self, pi, pin, config_file='buzzer.json'):
        self.pi = pi
        self.pin = pin
        self.config_file = config_file
        self.pi.set_mode(self.pin, pigpio.OUTPUT)
        self.save_config()
        # self.play_hello() # remove auto play hello

    def save_config(self):
        config = {'pin': self.pin}
        with open(self.config_file, 'w') as f:
            json.dump(config, f)

    def play_hello(self):
        # A simple melody
        notes = [
            (262, 0.2),  # C4
            (294, 0.2),  # D4
            (330, 0.2),  # E4
            (349, 0.2),  # F4
            (392, 0.2),  # G4
            (440, 0.2),  # A4
            (494, 0.2),  # B4
            (523, 0.4),  # C5
        ]
        for note, duration in notes:
            self.pi.set_PWM_frequency(self.pin, note)
            self.pi.set_PWM_dutycycle(self.pin, 128)  # 50% duty cycle
            time.sleep(duration)
        self.pi.set_PWM_dutycycle(self.pin, 0)  # Stop PWM

    def play_sound(self, frequency, duration):
        self.pi.set_PWM_frequency(self.pin, frequency)
        self.pi.set_PWM_dutycycle(self.pin, 128)  # 50% duty cycle
        time.sleep(duration)
        self.pi.set_PWM_dutycycle(self.pin, 0)  # Stop PWM

    def off(self):
        self.pi.set_PWM_dutycycle(self.pin, 0)  # Stop PWM

class MusicBuzzer(Buzzer):
    def __init__(self, pi, pin, config_file='buzzer.json'):
        super().__init__(pi, pin, config_file)
        self.notes = {
            # Middle C
            'a': 262, 's': 294, 'd': 330, 'f': 349, 'g': 392, 'h': 440, 'j': 494,
            # High C
            'q': 523, 'w': 587, 'e': 659, 'r': 698, 't': 784, 'y': 880, 'u': 988,
            # Low C
            'z': 131, 'x': 147, 'c': 165, 'v': 175, 'b': 196, 'n': 220, 'm': 247,
        }

    def play_music(self):
        print("Press keys to play notes. Press 'esc' to quit.")
        print("Middle C: a, s, d, f, g, h, j")
        print("High C:   q, w, e, r, t, y, u")
        print("Low C:    z, x, c, v, b, n, m")
        input("Press Enter to start...")

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            last_char = None
            while True:
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    char = sys.stdin.read(1)
                    if ord(char) == 27:  # ESC key
                        break
                    if char in self.notes:
                        if char != last_char:
                            self.pi.set_PWM_frequency(self.pin, self.notes[char])
                            self.pi.set_PWM_dutycycle(self.pin, 128)
                            last_char = char
                else:
                    self.pi.set_PWM_dutycycle(self.pin, 0)
                    last_char = None

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            self.off()
```

## 4. Create the command-line interface

This file provides a simple CLI for initializing the buzzer.

**File:** `pi0buzzer/src/pi0buzzer/__main__.py`

```python
import click
import pigpio
import json
from .driver import Buzzer, MusicBuzzer

@click.group()
def cli():
    pass

@cli.command()
@click.argument('pin', type=int)
def init(pin):
    """Initializes the buzzer on the specified GPIO pin."""
    pi = pigpio.pi()
    if not pi.connected:
        raise click.ClickException("Could not connect to pigpio daemon. Is it running?")
    buzzer = Buzzer(pi, pin)
    buzzer.off()
    pi.stop()
    click.echo(f"Buzzer initialized on GPIO {pin} and config saved to buzzer.json")

@cli.command()
@click.option('--pin', type=int, default=None, help='GPIO pin for the buzzer')
def playmusic(pin):
    """Play music with the buzzer using the keyboard."""
    pi = pigpio.pi()
    if not pi.connected:
        raise click.ClickException("Could not connect to pigpio daemon. Is it running?")

    if pin is None:
        try:
            with open('buzzer.json', 'r') as f:
                config = json.load(f)
                pin = config['pin']
        except FileNotFoundError:
            raise click.ClickException("Buzzer not initialized. Please run 'pi0buzzer init <pin>' first or specify a pin with --pin.")

    music_buzzer = MusicBuzzer(pi, pin)
    music_buzzer.play_music()
    pi.stop()

if __name__ == '__main__':
    cli()
```

## 5. Create the `README.md` file

This file provides documentation for the user.

**File:** `pi0buzzer/README.md`

```markdown
# pi0buzzer

A simple buzzer driver for Raspberry Pi.

## Installation

Install the driver using `uv`:

```bash
# Make sure you are in the NinjaRobotV3 directory
uv pip install -e pi0buzzer
```

## Usage

### From the Command Line

You can initialize the buzzer using the `pi0buzzer` command:

```bash
# Initialize the buzzer on GPIO 18
pi0buzzer init 18
```

This will play a short "Hello World" sound and create a `buzzer.json` file with the pin number.

### Play Music

After initializing the buzzer, you can play music with it using your keyboard:

```bash
pi0buzzer playmusic
```

### As a Library

You can also use the `Buzzer` class in your Python scripts:

```python
import pigpio
import time
from pi0buzzer.driver import Buzzer

# Initialize pigpio
pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("Could not connect to pigpio daemon.")

# Initialize the buzzer (this will play the "Hello World" sound)
buzzer = Buzzer(pi, 18)

# Play a custom sound
try:
    while True:
        buzzer.play_sound(440, 0.5) # Play 440 Hz for 0.5 seconds
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    buzzer.off()
    pi.stop()

```
