# NinjaRobotV3 Development Guide

This guide provides instructions on how to control the various hardware components of the NinjaRobotV3, including servos, the LCD display, the buzzer, and the distance sensor.

## 1. Installation and Setup

Before running any scripts, you need to install the necessary drivers for each component. These drivers are provided as local Python packages. It is recommended to use `uv` for installation.

First, ensure the `pigpio` daemon is running, as it is required by all drivers:

```bash
# Install pigpio if you haven't already
sudo apt update
sudo apt install pigpio

# Start and enable the pigpio daemon
sudo systemctl start pigpiod
sudo systemctl enable pigpiod
```

Next, install each driver in editable mode. This allows you to make changes to the driver code and have them immediately reflected.

```bash
# From the NinjaRobotV3 directory
uv pip install -e ./pi0buzzer
uv pip install -e ./pi0disp
uv pip install -e ./piservo0
uv pip install -e ./vl53l0x_pigpio
```

## 2. Configuration Files

The main application script, `main_robot_control.py`, is data-driven. It reads the GPIO pin configurations from `servo.json` and `buzzer.json` located in the root directory. Before running the main script, ensure these files are correctly configured.

- **`servo.json`**: This file should contain a list of all servo motor configurations. The `piservo0 calib` command automatically generates and updates this file.
- **`buzzer.json`**: This file contains the GPIO pin for the buzzer. The `pi0buzzer init <pin>` command creates this file.

## 3. Controlling the Modules

The following sections explain how to use each driver in your Python code.

### 2.1 Servo Control (`piservo0`)

The `piservo0` library allows for precise control of multiple servo motors. It supports calibration to account for individual servo differences.

**Key Classes:**
- `PiServo`: Basic servo control.
- `CalibrableServo`: Extends `PiServo` with calibration capabilities.
- `MultiServo`: Controls a group of servos synchronously.

**Example: Moving a single servo**

```python
import time
import pigpio
from piservo0 import CalibrableServo

# --- Configuration ---
SERVO_PIN = 17  # GPIO pin for the servo

# --- Initialization ---
pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("Could not connect to pigpio daemon.")

try:
    # Initialize a single calibrable servo
    # It automatically loads calibration data from 'servo.json' if it exists.
    servo = CalibrableServo(pi, SERVO_PIN)

    print("Moving to center (0 degrees)...")
    servo.move_angle(0)
    time.sleep(1)

    print("Moving to minimum angle (-90 degrees)...")
    servo.move_angle(-90)
    time.sleep(1)

    print("Moving to maximum angle (90 degrees)...")
    servo.move_angle(90)
    time.sleep(1)

finally:
    print("Turning off servo.")
    servo.off()
    pi.stop()
```

### 2.2 LCD Display Control (`pi0disp`)

The `pi0disp` library is a high-performance driver for ST7789V-based displays. It uses optimizations like dirty-region updates to achieve smooth animations.

**Key Class:**
- `ST7789V`: The main driver class for the display.

**Example: Displaying an image**

```python
from pi0disp import ST7789V
from PIL import Image, ImageDraw

# Initialize the display using a 'with' statement for automatic cleanup
# The driver handles the pigpio connection internally.
with ST7789V() as lcd:
    # Create a new image with a black background
    image = Image.new("RGB", (lcd.width, lcd.height), "black")
    draw = ImageDraw.Draw(image)

    # Draw a blue rectangle with a white outline
    draw.rectangle(
        (30, 30, lcd.width - 30, lcd.height - 30),
        fill="blue",
        outline="white",
        width=5
    )
    
    draw.text((50, 50), "Hello, NinjaRobot!", fill="white")

    # Display the image on the LCD
    lcd.display(image)

    # The display will automatically turn off when the 'with' block is exited.
```

### 2.3 Buzzer Control (`pi0buzzer`)

The `pi0buzzer` library provides a simple interface to control a buzzer.

**Key Class:**
- `Buzzer`: The main class for buzzer control.

**Example: Playing a sound**

```python
import pigpio
import time
from pi0buzzer.driver import Buzzer

# --- Configuration ---
BUZZER_PIN = 18  # GPIO pin for the buzzer

# --- Initialization ---
pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("Could not connect to pigpio daemon.")

try:
    # Initialize the buzzer
    buzzer = Buzzer(pi, BUZZER_PIN)

    print("Playing a C4 note (262 Hz) for 0.5 seconds.")
    buzzer.play_sound(262, 0.5)
    time.sleep(1)

    print("Playing a short melody.")
    buzzer.play_hello() # Plays a predefined melody

finally:
    print("Turning off buzzer.")
    buzzer.off()
    pi.stop()
```

### 2.4 Distance Sensor Control (`vl53l0x_pigpio`)

The `vl53l0x_pigpio` library is used to get distance measurements from the VL53L0X Time-of-Flight sensor.

**Key Class:**
- `VL53L0X`: The main driver class for the sensor.

**Example: Getting a distance measurement**

```python
import pigpio
from vl53l0x_pigpio import VL53L0X

# --- Initialization ---
pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("Could not connect to pigpio daemon.")

try:
    # Initialize the sensor using a 'with' statement
    # It automatically loads calibration from '~/vl53l0x.json' if it exists.
    with VL53L0X(pi) as tof:
        distance = tof.get_range()
        if distance > 0:
            print(f"Distance measured: {distance} mm")
        else:
            print("Measurement out of range or invalid.")
finally:
    pi.stop()
```

## 3. Integrated Example (`main_robot_control.py`)

The `main_robot_control.py` script demonstrates how to use all these drivers together. It initializes all the components and performs a simple sequence of actions:

1.  Initializes `pigpio`.
2.  Sets up the servo, display, buzzer, and distance sensor.
3.  Displays a "Ready!" message on the screen.
4.  Plays a startup sound.
5.  Moves the servo to the center position.
6.  Takes a distance measurement and displays it.
7.  Cleans up all resources gracefully on exit.

To run the example:

```bash
python main_robot_control.py
```

## 4. Utility Scripts

Beyond the core drivers, the `pi0ninja_v3` package contains high-level utility scripts for direct robot interaction.

### 4.1 Servo Movement Recorder

The `pi0ninja_v3.movement_recorder` module is a command-line tool for designing, saving, and executing complex servo movement sequences. It provides an interactive menu to record movements step-by-step, modify them with a safe, non-destructive editor, and play them back with looping and interruption capabilities.

All movement data is stored in `servo_movement.json` in the project root. The tool is an excellent example of how to integrate the `piservo0` library for multi-servo control.

To run the tool:
```bash
uv run python -m pi0ninja_v3.movement_recorder
```

### 4.2 Facial Expression Viewer

The `pi0ninja_v3.show_faces` module provides an interactive viewer for all animations in the `facial_expressions` library.

Its architecture serves as a good example of a persistent, non-blocking main loop. The idle animation (with random blinks) runs continuously while a non-blocking listener waits for keyboard input. This separates the robot's default state from temporary, one-shot actions (like playing a specific emotional animation), which are triggered from a standard blocking menu. This design avoids the state corruption issues that can arise from using exceptions for control flow.

To run the tool:
```bash
uv run python -m pi0ninja_v3.show_faces
```
