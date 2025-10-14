# NinjaRobotV3: Your First Step into Robotics

## 1. Introduction

Welcome to the world of robotics! The NinjaRobotV3 is a small, friendly robot that you can build yourself. It's powered by a tiny computer called a Raspberry Pi. This project is designed to be a fun and engaging way to learn the basics of how hardware (like motors and sensors) and software (the code) work together.

**What can the NinjaRobot do?**
- **Move:** It walks and moves its arms using eight different motors.
- **See:** It has a laser "eye" to measure how far away things are.
- **Show Emotions:** It has a screen for a face that can display different expressions.
- **Make Sounds:** A small buzzer lets it beep and play simple tunes.
- **Think:** It has an advanced AI "brain" (powered by Google's Gemini) that lets you control it using text or voice commands in a web browser.

By building this robot, you will get a hands-on introduction to electronics, programming, and artificial intelligence, even if you've never written a line of code before!

---

## 2. Hardware Requirements

Here is a list of the parts you'll need to build your robot. Each component has a special job.

| Component | Quantity | What it does |
| :--- | :--- | :--- |
| Raspberry Pi Zero 2W | 1 | The robot's "brain"—a small computer that runs all the software. |
| Ninja Robot customized expansion HAT & Power Management HAT | 1 set | Special circuit boards that make it easy to connect all the parts to the Pi. |
| SG90 180° servo | 4 | The robot's "muscles" for its legs, allowing it to stand and move. |
| DSpower M005 nano servo | 4 | Smaller "muscles" for the robot's arms. |
| VL53L0X laser distance sensor | 1 | The robot's "eyes"—it uses a laser to see how far away objects are. |
| 2.4-inch SPI TFT Display Module | 1 | The robot's "face," which can show expressions and information. |
| Buzzer | 1 | The robot's "voice," allowing it to make sounds and beeps. |

### Hardware Connections

The Ninja Robot HAT makes it easy to connect everything. Here’s a reference for how the parts are wired. You shouldn't need to change this, but it's helpful for understanding how it works.

#### **Servos (Motors)**

| Body Part | Connected to GPIO Pin |
| :--- | :--- |
| Left Leg | 17 |
| Right Leg | 27 |
| Left Foot | 22 |
| Right Foot | 5 |
| Left Shoulder | 25 |
| Right Shoulder | 23 |
| Left Arm | 21 |
| Right Arm | 24 |

#### **2.4 inch SPI Display (Face)**

| Pin | Ninja HAT Pin Label |
| :--- | :--- |
| GND | GND |
| VCC | 3V3 |
| SCL| SCLK |
| SDA | MOSI |
| RST | 19 |
| DC | 18 |
| CS | CE0 |
| BL | 20 |

#### **Buzzer (Voice)**

| Buzzer Pin | Connected to GPIO Pin |
| :--- | :--- |
| Signal | 26 |

#### **VL53L0X Sensor (Eyes)**

This sensor uses a connection called I2C, which has standard pins.

| Pin | Ninja HAT Pin Label |
| :--- | :--- |
| SDA | SDA (I2C) |
| SCL | SCL (I2C) |
| VCC | 3V (I2C) |
| GND | GND (I2C) |

---

## 3. Software Installation Guide

Now let's get the software—the instructions that tell the robot what to do—set up on your Raspberry Pi.

#### **Step 1: Install Raspberry Pi OS**

*   **What to do:** Use the official Raspberry Pi Imager to install the "Raspberry Pi OS (Legacy, 64-bit)" on your microSD card.
*   **Why:** The operating system is the foundation for all other software. We use the 64-bit Legacy version for the best compatibility with the robot's drivers.
*   **How:** Follow the official guide here: [https://www.raspberrypi.com/software/](https://www.raspberrypi.com/software/)

#### **Step 2: Update Your System**

*   **What to do:** Open a terminal on your Raspberry Pi and run this command:
    ```bash
    sudo apt update && sudo apt upgrade -y
    ```
*   **Why:** This command downloads the latest security updates and software improvements for your Pi's operating system, keeping it healthy and secure.

#### **Step 3: Enable Hardware Interfaces (I2C and SPI)**

*   **What to do:** Run the configuration tool with this command:
    ```bash
    sudo raspi-config
    ```
    In the menu, go to `3 Interface Options` and enable `I3 I2C` and `I4 SPI`.
*   **Why:** The robot's "eyes" (distance sensor) and "face" (display) use special communication methods called I2C and SPI. This step turns them on so the Pi can talk to them.

#### **Step 4: Install Essential Tools**

*   **What to do:** Install `git` and `pigpio` with this command:
    ```bash
    sudo apt install git pigpio -y
    ```
*   **Why:**
    *   `git` is a tool used to download code from the internet, which we'll use to get the NinjaRobot software.
    *   `pigpio` is a library that is very good at controlling the robot's motors and buzzer with precise timing.

#### **Step 5: Start the `pigpio` Service**

*   **What to do:** Run these two commands, one after the other:
    ```bash
    sudo systemctl start pigpiod
    sudo systemctl enable pigpiod
    ```
*   **Why:** This starts the `pigpio` service and sets it to launch automatically every time you turn on your Pi. This is necessary for the motors and buzzer to work.

#### **Step 6: Install `uv` (Python Package Manager)**

*   **What to do:** Run this command to install `uv`, a modern tool for managing Python software.
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
    After it finishes, close and reopen your terminal.
*   **Why:** The robot's software is written in Python. `uv` is a fast and easy way to install the specific Python libraries the robot needs to function.

#### **Step 7: Download the NinjaRobotV3 Project**

*   **What to do:** Use `git` to download the robot's source code from GitHub.
    ```bash
    git clone https://github.com/Nilcreator/NinjaRobotV3.git
    ```
    This will create a new folder called `NinjaRobotV3`. Now, move into that folder:
    ```bash
    cd NinjaRobotV3
    ```
*   **Why:** This command copies all the robot's code, guides, and files from its online home onto your Raspberry Pi.

#### **Step 8: Install the Robot's Python Libraries**

*   **What to do:** This is the final software installation step. Make sure you are in the `NinjaRobotV3` directory and run this command:
    ```bash
    uv pip install -e ./pi0ninja_v3 -e ./piservo0 -e ./pi0disp -e ./vl53l0x_pigpio -e ./pi0buzzer
    ```
*   **Why:** This command uses `uv` to install all the different software drivers for the robot's parts (servos, display, etc.). The `-e` makes them "editable," which means you can easily modify the code later if you want to experiment.

---

## 4. User Guide: Testing and Controlling Your Robot

Your robot is built and the software is installed! Let's run some simple tests and then bring your robot to life.

### Testing Individual Parts

These commands help you check that each component is working correctly.

#### **Test 1: The Buzzer (Voice)**

*   **What to do:** Run this command to test the buzzer. It should play a short "Hello World" sound.
    ```bash
    uv run pi0buzzer init 26
    ```
*   **Why:** This command tells the buzzer driver (`pi0buzzer`) to initialize on GPIO pin 26 and make a sound.

#### **Test 2: The Display (Face)**

*   **What to do:** Run this command to start a test animation on the display. You should see a ball bouncing around the screen. Press `Ctrl+C` to stop.
    ```bash
    uv run pi0disp test
    ```
*   **Why:** This runs the display driver's (`pi0disp`) built-in test, confirming that the screen is connected and working correctly.

#### **Test 3: The Distance Sensor (Eyes)**

*   **What to do:** Run this command to take 5 distance readings.
    ```bash
    uv run vl53l0x_pigpio get --count 5
    ```
*   **Why:** This tells the sensor driver (`vl53l0x_pigpio`) to measure the distance to the nearest object and print it in millimeters.

#### **Test 4: The Servos (Muscles)**

*   **What to do:** Let's test the left leg servo. Run this command to move it to its center position.
    ```bash
    uv run piservo0 servo 17 0
    ```
    You can try other angles, like `-90` or `90`.
*   **Why:** This command tells the servo driver (`piservo0`) to move the servo on GPIO pin 17 to angle 0 (the middle). You can test other servos by changing the pin number (e.g., `27` for the right leg).

### Bringing Your Robot to Life: The Web Interface

This is the most exciting part! You will now start the main web server that lets you control your robot from a browser and chat with its AI brain.

#### **Step 1: Get Your Gemini API Key**

*   **What to do:**
    1.  Go to Google AI Studio: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
    2.  Click "**Create API key**" and copy the long string of letters and numbers. This is your key.
*   **Why:** The Gemini API Key is like a secret password that allows your robot to connect to Google's powerful AI model.

#### **Step 2: Set Up a Public URL for Remote Access (One-Time Setup)**

*   **What to do:** To use the voice chat from any device or control your robot from outside your home network, you need a secure, public URL. This feature uses a tool called `ngrok`. You only need to set this up once.
    1.  Go to the ngrok dashboard and sign up for a free account: [https://dashboard.ngrok.com/signup](https://dashboard.ngrok.com/signup)
    2.  On your dashboard, find your **Authtoken**.
    3.  In your Raspberry Pi terminal, inside the `NinjaRobotV3` folder, run this command, replacing `<YOUR_AUTHTOKEN>` with the token you copied:
        ```bash
        ./ngrok config add-authtoken <YOUR_AUTHTOKEN>
        ```
*   **Why:** This command securely links the `ngrok` tool on your Pi to your account. This allows the web server to create a secure `https://` address, which is required by modern browsers to use the microphone for voice commands.

#### **Step 3: Start the Web Server**

*   **What to do:** In the terminal, from the `NinjaRobotV3` directory, run this command:
    ```bash
    uv run web-server
    ```
*   **Why:** This command starts the main application. It initializes all the robot's hardware, creates the public `ngrok` URL, and starts the web interface.

#### **Step 4: Connect and Chat!**

*   **What to do:** When the server starts, it will print several URLs. To use voice chat, you **must** use the secure public URL.
    1. Look for the line that says `Secure Public URL (HTTPS): https://<random-string>.ngrok-free.app` and open that URL in a browser.
    2. The first time you open the page, a popup will ask for your Gemini API Key. Paste the key you got in Step 1.
    3. The interface will load. You can now talk to your robot!

*   **How to Interact:**
    *   **Text Chat:** Type a command like "say hello" or "raise your left arm" into the chat box and press Enter.
    *   **Voice Chat:** Click the microphone icon (🎤). It will turn red while recording. Speak your command, and it will stop automatically when you pause. Your command will be sent to the robot.

**Congratulations!** Your NinjaRobot is now fully built and ready for action. Have fun exploring the world of robotics!
