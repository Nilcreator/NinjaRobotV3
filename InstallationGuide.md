# NinjaRobotV3: Your First Step into Robotics

## 1. Introduction

Welcome to the world of robotics! The NinjaRobotV3 is a small, friendly robot that you can build yourself. It's powered by a tiny computer called a Raspberry Pi. This project is designed to be a fun and engaging way to learn the basics of how hardware (like motors and sensors) and software (the code) work together.

**What can the NinjaRobot do?**
- **Move:** It walks and moves its arms using eight different motors.
- **See:** It has a laser "eye" to measure how far away things are.
- **Show Emotions:** It has a screen for a face that can display different expressions.
- **Make Sounds:** A small buzzer lets it beep and play simple tunes.
- **Think:** It has an advanced AI "brain" (powered by Google's Gemini) that lets you control it using text commands in a web browser.

By building this robot, you will get a hands-on introduction to electronics, programming, and artificial intelligence, even if you've never written a line of code before!

---

## 2. Hardware Requirements

(This section remains the same)

---

## 3. Software Installation Guide

(Steps 1-6 remain the same)

#### **Step 7: Install the Robot's Python Libraries**

*   **What to do:** This is the final software installation step. Make sure you are in the `NinjaRobotV3` directory and run this command:
    ```bash
    uv pip install -e ./pi0ninja_v3 -e ./piservo0 -e ./pi0disp -e ./vl53l0x_pigpio -e ./pi0buzzer
    ```
*   **Why:** This command uses `uv` to install all the different software drivers for the robot's parts.

---

## 4. User Guide: Testing Your Robot

(This section remains the same)

---

## 5. Bringing Your Robot to Life: The Web Interface

This is the most exciting part! You will now start the main web server that lets you control your robot from a browser and chat with its AI brain.

#### **Step 1: Get Your Gemini API Key**

*   **What to do:**
    1.  Go to Google AI Studio: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
    2.  Click "**Create API key**" and copy the long string of letters and numbers. This is your key.
*   **Why:** The Gemini API Key is like a secret password that allows your robot to connect to Google's powerful AI model.

#### Step 2: Set Up a Public URL (One-Time Setup, Optional)

*   **What to do:** The robot's web server can create a secure, public URL so you can access it from outside your local network. This feature uses a tool called `ngrok`. You only need to perform this one-time setup to link it to a free account.
    1.  Go to the ngrok dashboard and sign up: [https://dashboard.ngrok.com/signup](https://dashboard.ngrok.com/signup)
    2.  On your dashboard, find your "**Authtoken**".
    3.  In your Raspberry Pi terminal, inside the `NinjaRobotV3` folder, run this command, replacing `<YOUR_AUTHTOKEN>` with the token you copied:
        ```bash
        ./ngrok config add-authtoken <YOUR_AUTHTOKEN>
        ```
*   **Why:** This command securely links the `ngrok` tool on your Pi to your account. You only need to do this once for the remote access feature to work.

#### Step 3: Start the Web Server

*   **What to do:** In the terminal, from the `NinjaRobotV3` directory, run this command:
    ```bash
    uv run web-server
    ```
*   **Why:** This command starts the main application, initializing all the robot's hardware and starting the web interface.

#### Step 4: Connect and Chat!

*   **What to do:** When the server starts, it will print the URLs you can use. 
    1. Open a web browser on a computer or phone on the same network and go to one of the local URLs shown (e.g., `http://<your-pi-ip-address>:8000`).
    2. If you configured `ngrok`, you can also use the "Secure Public URL" to access the robot from anywhere.
    3. The first time you open the page, a popup will ask for your Gemini API Key. Paste the key you got in Step 1.
    4. The interface will load. You can now type commands to your robot in the chat box!

---

## 6. Advanced Fun: Recording Your Own Movements

(This section remains the same)

**Congratulations!** If all the tests worked, your NinjaRobot is fully built and ready for action. For more detailed information on using the web interface, please read the **`NinjaUserGuide.md`**.