# NinjaRobotV3: Your First Step into Robotics

## 1. Introduction

Welcome to the world of robotics! The NinjaRobotV3 is a small, friendly robot that you can build yourself. It's powered by a tiny computer called a Raspberry Pi. This project is designed to be a fun and engaging way to learn the basics of how hardware (like motors and sensors) and software (the code) work together.

**What can the NinjaRobot do?**
- **Move:** It walks and moves its arms using eight different motors.
- **See:** It has a laser "eye" to measure how far away things are.
- **Show Emotions:** It has a screen for a face that can display different expressions.
- **Make Sounds:** A small buzzer lets it beep and play simple tunes.
- **Think:** It has an advanced AI "brain" (powered by Google's Gemini) that lets you control it by talking to it through a web browser on your phone or computer.

By building this robot, you will get a hands-on introduction to electronics, programming, and artificial intelligence, even if you've never written a line of code before!

---

## 2. Hardware Requirements

This is the list of parts you'll need to build your robot. Each part has a special job.

| Part | Quantity | What it does |
| :--- | :--- | :--- |
| Raspberry Pi Zero 2W | 1 | This is the robot's **brain**. It's a tiny computer that runs all the software. |
| Ninja Robot HATs | 1 set | These are special circuit boards that sit on top of the brain, making it easy to connect all the other parts without messy wires. |
| SG90 180° Servo | 4 | These are the robot's **leg and foot muscles**, allowing it to stand and move. |
| DSpower M005 Nano Servo | 4 | These are the robot's **arm and shoulder muscles**, allowing it to wave. |
| VL53L0X Laser Sensor | 1 | These are the robot's **eyes**. It uses a safe laser to see how far away things are. |
| 2.4-inch SPI TFT Display | 1 | This is the robot's **face**. It's a small screen that can show expressions. |
| Buzzer | 1 | This is the robot's **voice box**. It makes beeps and sounds. |

### Hardware Connections (Wiring)

The Ninja Robot HATs make wiring simple. You just need to plug the components into the correct ports. These tables show you which part connects where.

#### **Servos (Muscles)**

| Function | Connects to GPIO Pin |
| :--- | :--- |
| Left Leg | 17 |
| Right Leg | 27 |
| Left Foot | 22 |
| Right Foot | 5 |
| Left Shoulder | 25 |
| Right Shoulder | 23 |
| Left Arm | 21 |
| Right Arm | 24 |

#### **2.4-inch SPI Display (Face)**

| Display Pin | Ninja HAT Pin Label |
| :--- | :--- |
| GND | GND |
| VCC | 3V3 |
| CLK (SCL) | D11 (SCLK) |
| DIN (SDA) | D10 (MOSI) |
| RST | D24 (GPIO 19) |
| DC | D25 (GPIO 18) |
| CS | D8 (CE0) |
| BL | D18 (GPIO 20) |

#### **Buzzer (Voice Box)**

| Function | Connects to GPIO Pin |
| :--- | :--- |
| Signal | 26 |

#### **VL53L0X Sensor (Eyes)**

| Sensor Pin | Ninja HAT Pin Label |
| :--- | :--- |
| SDA | SDA (I2C) |
| SCL | SCL (I2C) |
| VCC | 3V (I2C) |
| GND | GND (I2C) |

---

## 3. Software Installation Guide

Now let's get the robot's brain ready by installing its software. Follow these steps carefully.

#### **Step 1: Install the Operating System**

*   **What to do:** First, you need to install the operating system for your Raspberry Pi. The official "Raspberry Pi Imager" is the easiest way to do this. Download it on your main computer and follow the instructions to flash "Raspberry Pi OS" onto your microSD card.
*   **Why:** The operating system (OS) is the core software that runs the computer. It's like Windows, macOS, or Android, but for your robot.

#### **Step 2: Update the System**

*   **What to do:** Once your Raspberry Pi is booted up and connected to the internet, open the Terminal and type the following command, then press Enter:
    ```bash
    sudo apt update && sudo apt upgrade -y
    ```
*   **Why:** This command downloads and installs the latest security updates and software improvements for your robot's OS, just like updating your phone or computer.

#### **Step 3: Enable Hardware Communication**

*   **What to do:** The robot's screen and sensors use special communication channels called SPI and I2C. We need to turn them on. Type this command and press Enter:
    ```bash
    sudo raspi-config
    ```
    Use the arrow keys to navigate the menu:
    1.  Go to `3 Interface Options`.
    2.  Select `I4 SPI` and choose `<Yes>`.
    3.  Select `I5 I2C` and choose `<Yes>`.
    4.  Go to `Finish` to exit.
*   **Why:** This tells the Raspberry Pi's brain to activate the physical ports that the screen (SPI) and distance sensor (I2C) use to talk to it.

#### **Step 4: Install Essential Tools**

*   **What to do:** We need a few more tools. Type this command and press Enter:
    ```bash
    sudo apt install git pigpio -y && curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
*   **Why:**
    *   `git`: This tool is used to download code from websites like GitHub.
    *   `pigpio`: This is a special library that is very good at controlling the robot's motors precisely.
    *   `uv`: This is a fast, modern tool we will use to manage all the Python software components of the robot.

#### **Step 5: Start the Motor Control Service**

*   **What to do:** Now we need to start the `pigpio` service we just installed.
    ```bash
    sudo systemctl start pigpiod && sudo systemctl enable pigpiod
    ```
*   **Why:** This starts the motor control service and, importantly, tells the robot to start it automatically every time it boots up.

#### **Step 6: Download the NinjaRobot Code**

*   **What to do:** It's time to download the robot's project files.
    ```bash
    git clone https://github.com/Nilcreator/NinjaRobotV3.git
    cd NinjaRobotV3
    ```
*   **Why:** The first command uses `git` to copy the entire NinjaRobotV3 project from GitHub to your Raspberry Pi. The second command moves you inside the project folder you just downloaded.

#### **Step 7: Install the Robot's Python Libraries**

*   **What to do:** This is the final software installation step. Make sure you are in the `NinjaRobotV3` directory and run this command:
    ```bash
    uv pip install -e ./pi0ninja_v3 -e ./piservo0 -e ./pi0disp -e ./vl53l0x_pigpio -e ./pi0buzzer
    ```
*   **Why:** This command uses `uv` to install all the different software drivers for the robot's parts (the main controller, servos, display, sensor, and buzzer). The `-e` flag installs them in "editable" mode, which means if you decide to change the code later, your changes will be used immediately. If you get a `uv: command not found` error, try restarting your terminal or running `source ~/.profile` first.

---

## 4. User Guide: Testing Your Robot

After assembly and software installation, it's a good idea to test each part to make sure everything is working correctly. Run these commands from the `NinjaRobotV3` directory in your terminal.

#### **Test 1: The Buzzer (Voice Box)**

*   **What to do:** Let's test the buzzer. This command tells the robot that the buzzer is on pin 26.
    ```bash
    uv run pi0buzzer init 26
    ```
*   **What to expect:** You should hear a short "Hello World" sound. If you do, it's working!

#### **Test 2: The Display (Face)**

*   **What to do:** Now for the face. This command runs a performance test.
    ```bash
    uv run pi0disp test
    ```
*   **What to expect:** You should see animated, colorful balls bouncing around on the screen. If you see them, your display is working! Press `Ctrl` + `C` on your keyboard to stop the test.

#### **Test 3: The Distance Sensor (Eyes)**

*   **What to do:** Time to test the eyes. This command will take 10 distance measurements.
    ```bash
    uv run vl53l0x_pigpio get
    ```
*   **What to expect:** The terminal will print out distance readings in millimeters. Try putting your hand in front of the sensor and see the numbers change.

#### **Test 4: The Servos (Muscles)**

*   **What to do:** Let's test one of the leg motors. This command tells the servo on pin 17 (the left leg) to move to the 0-degree (center) position.
    ```bash
    uv run piservo0 servo 17 0
    ```
*   **What to expect:** You should see the left leg servo move. You can test the other servos by changing the pin number and the angle. For example, to test the right leg (pin 27) and move it to 45 degrees, you would run:
    ```bash
    uv run piservo0 servo 27 45
    ```
    Refer to the hardware table to get the pin number for each servo.

---

## 5. Bringing Your Robot to Life: The Web Interface

This is the most exciting part! You will now start the main web server that lets you control your robot from a browser and talk to its AI brain.

#### **Step 1: Get Your Gemini API Key**

*   **What to do:**
    1.  Go to Google AI Studio: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
    2.  Click "**Create API key**" and copy the long string of letters and numbers. This is your key.
*   **Why:** The Gemini API Key is like a secret password that allows your robot to connect to Google's powerful AI model. This is what lets your robot understand you and talk back.

#### **Step 2: Set Up the Secure Tunnel (One-Time Setup)**

*   **What to do:** For your browser's microphone to work, it needs a secure `https://` connection. We use a tool called `ngrok` for this.
    1.  Go to the ngrok dashboard and sign up for a free account: [https://dashboard.ngrok.com/signup](https://dashboard.ngrok.com/signup)
    2.  On your dashboard, find your "**Authtoken**".
    3.  In your Raspberry Pi terminal, inside the `NinjaRobotV3` folder, run this command, replacing `<YOUR_AUTHTOKEN>` with the token you copied:
        ```bash
        ./ngrok config add-authtoken <YOUR_AUTHTOKEN>
        ```
*   **Why:** This command securely links the `ngrok` tool on your Pi to your account. You only need to do this once. From now on, the web server will handle `ngrok` automatically.

#### **Step 3: Start the Web Server**

*   **What to do:** In the terminal, from the `NinjaRobotV3` directory, run this command:
    ```bash
    uv run web-server
    ```
*   **Why:** This command starts the main application. It will initialize all the robot's hardware and start the web interface.

#### **Step 4: Connect and Talk!**

*   **What to do:** When the server starts, look for a line in the terminal output that looks like this:
    ```
    - For Voice (HTTPS): https://<random-string>.ngrok-free.app
    ```
    1.  Open a web browser on your computer or phone and go to that `https://` URL.
    2.  The first time you open it, a popup will ask for your Gemini API Key. Paste the key you got in Step 1.
    3.  The interface will load. Click the microphone icon to start talking to your robot!
*   **Why:** Using the secure `https://` link is essential. It proves to your browser that the connection is safe, which is a requirement for allowing microphone access.

---

## 6. Advanced Fun: Recording Your Own Movements

You can teach your robot custom dance moves or gestures! The `movement-recorder` tool lets you create sequences of servo movements and save them.

#### **Step 1: Start the Recorder**

*   **What to do:** In the terminal, from the `NinjaRobotV3` directory, run:
    ```bash
    uv run movement-recorder
    ```
*   **Why:** This starts the interactive tool for recording and playing back movements.

#### **Step 2: Understanding the Command Language**

When you record a new movement, you tell the servos where to go using a simple command string.

*   **The Format:** `[PIN_NUMBER]:[ANGLE]`
*   You can command multiple servos at once by separating them with a `/`.
    *   Example: `17:45/27:-45` (Move servo on pin 17 to 45 degrees AND servo on pin 27 to -45 degrees).
*   **Special Angle Shortcuts:**
    *   `C`: Center (0 degrees)
    *   `M`: Minimum angle (usually -90 degrees)
    *   `X`: Maximum angle (usually 90 degrees)
    *   Example: `22:C/5:C` (Center the two foot servos).
*   **Setting Speed:** You can add a speed prefix to a command.
    *   `S_`: Slow (takes 1 second)
    *   `M_`: Medium (takes 0.5 seconds) (This is the default if you don't specify)
    *   `F_`: Fast (takes 0.2 seconds)
    *   Example: `S_17:90/27:90` (Slowly move both leg servos to 90 degrees).

#### **Step 3: Using the Tool**

The tool has a simple menu:
1.  **Record new movement:** This will guide you step-by-step. You enter a command, see the robot move, and then choose to `Confirm & Next`, `Reset` the step, or `Finish Recording`. When you finish, you'll give the movement a name.
2.  **Modify existing movement:** Lets you edit a saved sequence.
3.  **Execute a movement:** Choose a saved movement and watch the robot perform it! You can even make it loop.
4.  **Clear movement:** Delete a saved movement.

**Congratulations!** If all the tests worked, your NinjaRobot is fully built and ready for action. For more detailed information on using the web interface, please read the **`NinjaUserGuide.md`**.
