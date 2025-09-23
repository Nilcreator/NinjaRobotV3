# NinjaRobotV3 User Guide

(Sections 1-2.4 remain the same)

### 2.5. `pi0ninja_v3` - Robot Control Hub

(Intro remains the same)

#### Web Control Interface

(Intro remains the same)

#### Ninja AI Agent

The web interface features a conversational AI agent powered by Google's Gemini model. You can type commands in natural language, and it will interpret your intent, perform actions, and answer questions.

**Capabilities:**
- **Text-Based Chat**: Type commands to the robot in real-time.
- **Voice Input**: Speak commands to the robot using your microphone.
- **Web Search**: The agent can search the internet to answer questions.

**1. Activating the AI Agent**

(This section remains the same)

**2. Interacting with the Agent**

Once the key is set, the chat interface will appear.

-   **Text Input**: Type a command in the chat box and press Enter or click the "Send" button.

-   **Voice Input**: Click the microphone button (🎤) to start recording. The button will turn red. Speak your command. The recording will stop automatically after 3 seconds of silence or manually if you click the button again. The button will turn green, and your voice command will be sent to the robot. Note: Your browser will ask for microphone permission the first time.

-   **System Log**: This box shows the AI's "thought process," including when it performs a web search or what physical actions it decides to take.

### 3. Accessing the Robot Remotely (Optional)

The web server automatically uses a tool called `ngrok` to create a secure, public URL for your robot's control panel. This is useful if you want to control your robot from a device that is not on the same local network.

**Step 1: First-Time Setup (One-Time Only)**

To enable this feature, you need to link `ngrok` to a free account.

1.  **Sign Up**: Go to the [ngrok dashboard](https://dashboard.ngrok.com/signup) and create a free account.
2.  **Add Authtoken**: Copy the authtoken from your ngrok dashboard and run this command in the `NinjaRobotV3` directory (replace `<YOUR_AUTHTOKEN>` with your actual token):
    ```bash
    ./ngrok config add-authtoken <YOUR_AUTHTOKEN>
    ```

**Step 2: Start the Server and Get the URL**

Now, just start the server as usual.

1.  **Run the NinjaRobot Web Server**:
    ```bash
    uv run web-server
    ```
2.  **Find Your Public URL**: When the server starts, look for a line in the terminal output like this:
    ```
    - Secure Public URL (HTTPS): https://<random-string>.ngrok-free.app
    ```

You can use this `https://` URL in any browser to access the robot's control panel from anywhere.

(Example Interactions remain the same)

#### Other Interactive Utilities

(Other utility sections remain the same)