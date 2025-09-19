# NinjaRobotV3 User Guide

This guide provides a comprehensive overview of the `pi0disp`, `piservo0`, `vl53l0x_pigpio`, and `pi0buzzer` libraries and how to use them within the `NinjaRobotV3` project.

## 1. Initial Setup

This project uses `uv` for managing Python virtual environments and dependencies.

### 1.1. Create and Activate the Virtual Environment

It is recommended to use a virtual environment for this project.

```bash
# Create the virtual environment
uv venv

# Activate the virtual environment
source .venv/bin/activate
```

### 1.2. Install Dependencies

Install the necessary packages for all libraries using `uv`.

```bash
# Install all dependencies from the subdirectories
uv pip install -e pi0disp
uv pip install -e piservo0
uv pip install -e vl53l0x_pigpio
uv pip install -e pi0buzzer
```

## 2. Using the Libraries

### 2.1. `pi0disp` - Display Driver

The `pi0disp` library is a high-speed driver for ST7789V-based displays on Raspberry Pi.

#### As a Library

You can use the `ST7789V` class to control the display in your Python scripts.

```python
from pi0disp import ST7789V
from PIL import Image, ImageDraw
import time

# Initialize the display
with ST7789V() as lcd:
    # Create an image with PIL
    image = Image.new("RGB", (lcd.width, lcd.height), "black")
    draw = ImageDraw.Draw(image)

    # Draw a blue circle
    draw.ellipse(
        (10, 10, lcd.width - 10, lcd.height - 10),
        fill="blue",
        outline="white"
    )

    # Display the image
    lcd.display(image)

    time.sleep(5)

    # Example of partial update
    draw.rectangle((50, 50, 100, 100), fill="red")
    lcd.display_region(image, 50, 50, 100, 100)

    time.sleep(5)
```

#### CLI Usage

The `pi0disp` command provides a simple CLI for testing the display.

```bash
# Run the ball animation demo
uv run pi0disp ball_anime

# Turn the display off
uv run pi0disp off
```

### 2.2. `piservo0` - Servo Motor Control

The `piservo0` library provides precise control over servo motors.

#### As a Library

Use the `PiServo` or `CalibrableServo` class to control your servos.

**Basic Usage (`PiServo`)**

```python
import time
import pigpio
from piservo0 import PiServo

PIN = 17

pi = pigpio.pi()
servo = PiServo(pi, PIN)

servo.move_pulse(1000)
time.sleep(0.5)

servo.move_max()
time.sleep(0.5)

servo.off()
pi.stop()
```

**Calibrated Usage (`CalibrableServo`)**

```python
import time
import pigpio
from piservo0 import CalibrableServo

PIN = 17

pi = pigpio.pi()
servo = CalibrableServo(pi, PIN) # Loads calibration from servo.json

servo.move_angle(45)  # Move to 45 degrees
time.sleep(1)

servo.move_center()
time.sleep(1)

servo.off()
pi.stop()
```

#### CLI Usage

The `piservo0` command allows for calibration and remote control.

**Calibration**

```bash
# Calibrate the servo on GPIO 17
uv run piservo0 calib 17
```

**API Server**

```bash
# Start the API server for servos on GPIO 17, 27, 22, 25
uv run piservo0 api-server 17 27 22 25
```

**API Client**

```bash
# Connect to the API server
uv run piservo0 api-client
```

### 2.3. `vl53l0x_pigpio` - Distance Sensor

The `vl53l0x_pigpio` library is a driver for the VL53L0X time-of-flight distance sensor.

#### As a Library

Use the `VL53L0X` class to get distance measurements.

```python
import pigpio
from vl53l0x_pigpio import VL53L0X
import time

pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("Could not connect to pigpio")

try:
    with VL53L0X(pi) as tof:
        distance = tof.get_range()
        if distance > 0:
            print(f"Distance: {distance} mm")
        else:
            print("Invalid data.")
finally:
    pi.stop()
```

#### CLI Usage

The `vl53l0x_pigpio` command provides tools for interacting with the sensor.

**Get Distance**

```bash
# Get 5 distance readings
uv run vl53l0x_pigpio get --count 5
```

**Performance Test**

```bash
# Run a performance test with 500 measurements
uv run vl53l0x_pigpio performance --count 500
```

**Calibration**

```bash
# Calibrate the sensor with a target at 150mm
uv run vl53l0x_pigpio calibrate --distance 150
```

### 2.4. `pi0buzzer` - Buzzer Driver

The `pi0buzzer` library is a simple driver for a piezo buzzer.

#### As a Library

You can use the `Buzzer` class to control the buzzer in your Python scripts.

```python
import pigpio
import time
from pi0buzzer.driver import Buzzer

# Initialize pigpio
pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("Could not connect to pigpio daemon.")

# Initialize the buzzer
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

#### CLI Usage

The `pi0buzzer` command provides a simple CLI for interacting with the buzzer.

**Initialization**

```bash
# Initialize the buzzer on GPIO 18
pi0buzzer init 18
```

**Play Music**

After initializing the buzzer, you can play music with it using your keyboard:

```bash
pi0buzzer playmusic
```

### 2.5. `pi0ninja_v3` - Robot Control Hub

`pi0ninja_v3` is the central library that brings together all the hardware drivers to create high-level robot behaviors. It includes several utility scripts for direct interaction.

#### Servo Movement Recorder

This is a powerful command-line tool that allows you to design, save, and play back complex servo movement sequences.

**How to Run**

To start the tool, run the following command from the project's root directory:

```bash
uv run python -m pi0ninja_v3.movement_recorder
```

(Details on how to use the recorder follow...)

#### Facial Expression Viewer

This is an interactive tool to preview all the available facial expressions on the robot's LCD screen.

**How to Run**

```bash
uv run python -m pi0ninja_v3.show_faces
```

**How to Use**

1.  **Idle State:** When the script starts, it will immediately display a continuous "idle" animation with random blinks.
2.  **Open Menu:** While the idle animation is running, press the `m` key to pause the animation and bring up the expression selection menu.
3.  **Select Expression:** Enter the number corresponding to the face you want to see.
4.  **Return to Idle:** After the animation finishes, the robot will automatically return to the continuous idle state.
5.  **Quit:** While the idle animation is running, press the `q` key to exit the program gracefully.

#### Robot Sound Player

This tool uses the buzzer to play sounds that correspond to the robot's facial expressions.

**How to Run**

```bash
uv run python -m pi0ninja_v3.robot_sound
```

**How to Use**

When you run the command, an interactive menu will appear. Enter the number corresponding to the emotion sound you want to hear. The available sounds are:
- Angry
- Confusing
- Cry
- Embarrassing
- Exciting
- Happy
- Idle
- Laughing
- Sad
- Scary
- Shy
- Sleepy
- Speaking
- Surprising

#### Distance Detector

This utility uses the VL53L0X time-of-flight sensor to measure the distance to an object.

**How to Run**

```bash
uv run python -m pi0ninja_v3.detect_distance
```

**How to Use**

Running the command will bring up a menu with two options:
1.  **Timed Detection:** Prompts you to enter a number of measurements to take and the time delay between them.
2.  **Continuous Detection:** Measures the distance five times per second, updating the value on a single line. Press `q` to stop.

---

### 2.5. `pi0ninja_v3` - ロボット制御ハブ

`pi0ninja_v3` ライブラリは、NinjaRobotの中央コントローラーであり、さまざまなドライバーを統合して複雑な動作を作成します。

#### サーボ動作レコーダー

これは、複雑なサーボ動作シーケンスを設計、保存、再生するための強力なコマンドラインツールです。

**実行方法**

ツールを起動するには、プロジェクトのルートディレクトリから次のコマンドを実行します。

```bash
uv run python -m pi0ninja_v3.movement_recorder
```

(レコーダーの使用方法の詳細は省略...)

#### 表情ビューア (Facial Expression Viewer)

これは、利用可能なすべての表情をロボットのLCD画面でプレビューするためのインタラクティブなツールです。

**実行方法**

```bash
uv run python -m pi0ninja_v3.show_faces
```

**使用方法**

1.  **アイドル状態:** スクリプトを開始すると、すぐにランダムなまばたきを伴う連続的な「アイドル」アニメーションが表示されます。操作するまで、ロボットはこの状態を維持します。
2.  **メニューを開く:** アイドルアニメーションの実行中に `m` キーを押すと、アニメーションが一時停止し、ターミナルに表情選択メニューが表示されます。
3.  **表情の選択:** 見たい顔に対応する番号を入力します。選択したアニメーションが5秒間再生されます。
4.  **アイドルに戻る:** アニメーションが終了すると、ロボットは自動的に連続的なアイドル状態に戻ります。
5.  **終了:** アイドルアニメーションの実行中に `q` キーを押すと、プログラムを正常に終了します。