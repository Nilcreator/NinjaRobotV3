
# NinjaRobotV3 User Guide

(Sections 1-2.4 remain the same)

### 2.5. `pi0ninja_v3` - Robot Control Hub

(Intro remains the same)

#### Web Control Interface

(Intro remains the same)

#### Ninja AI Agent

The web interface features a conversational AI agent powered by Google's Gemini model. You can talk to the robot in natural language, and it will interpret your intent, perform actions, and answer questions.

**Capabilities:**
- **Live Voice Chat**: Speak to the robot in real-time.
- **Web Search**: The agent can search the internet to answer questions.

**1. Activating the AI Agent**

(This section remains the same)

**2. Interacting with the Agent**

Once the key is set, the chat interface will appear.

-   **Voice Input (Recommended)**:
    - Click the **microphone (🎤) button** to start recording. It will turn red.
    - Speak your command.
    - Click the **microphone (🎤) button** again to stop. It will turn yellow while the robot thinks.
    - The robot will then respond and perform the action.

-   **Text Input**: You can always type a command in the chat box and press Enter or click Send. This works over both HTTP and HTTPS.

-   **System Log**: This box shows the AI's "thought process," including when it performs a web search or what physical actions it decides to take.

### 3. Enabling Voice Input with HTTPS (Automated with ngrok)

For security reasons, web browsers only allow microphone access on pages loaded over a secure `https://` connection. To make this seamless, the NinjaRobot web server now automatically uses a free tool called `ngrok` to create a secure tunnel for you.

**Step 1: First-Time Setup**

The first time you use the robot, you may need to set up `ngrok`.

1.  **Sign Up**: Go to the [ngrok dashboard](https://dashboard.ngrok.com/signup) and create a free account.
2.  **Download**: The `ngrok` executable should be downloaded for you, but if not, you can get it from the dashboard.
3.  **Add Authtoken**: You must connect `ngrok` to your account. Copy the authtoken from your ngrok dashboard and run this command in the `NinjaRobotV3` directory (replace `<YOUR_AUTHTOKEN>` with your actual token):
    ```bash
    ./ngrok config add-authtoken <YOUR_AUTHTOKEN>
    ```

**Step 2: Start the Server and Get the URL**

1.  **Run the NinjaRobot Web Server**:
    ```bash
    uv run web-server
    ```
2.  **Find Your HTTPS URL**: When the server starts, it will automatically launch `ngrok`. Look for a line in the terminal output like this:
    ```
    - For Voice (HTTPS): https://<random-string>.ngrok-free.app
    ```

Use this `https://` URL in your browser to access the robot's control panel. The microphone button for voice input will now be enabled automatically.

(Example Interactions remain the same)

#### Other Interactive Utilities

(Other utility sections remain the same)
