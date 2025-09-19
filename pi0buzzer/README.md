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