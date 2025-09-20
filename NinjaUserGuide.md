
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
    - Click the **microphone (🎤) button** to start and stop recording.
    - **IMPORTANT**: For the microphone to work, your browser requires a secure (HTTPS) connection to the robot. If you are accessing the robot via a standard `http://` address, the microphone button will be disabled or show an alert. For testing, a tool like `ngrok` can provide a temporary HTTPS address for your local server.
    - When listening is active, the button will change appearance and the input box will say "Listening...".
    - Speak your command, and click the button again to stop. The robot will process what you said.

-   **Text Input**: You can always type a command in the chat box and press Enter or click Send. This works over both HTTP and HTTPS.

-   **System Log**: This box shows the AI's "thought process," including when it performs a web search or what physical actions it decides to take.

### 3. Enabling Voice Input with HTTPS (ngrok)

For security reasons, web browsers only allow microphone access on pages loaded over a secure `https://` connection. To use the voice input feature, you need to create a secure tunnel to your robot's web server using a free tool called `ngrok`.

**Step 1: Install and Configure ngrok**

1.  **Sign Up**: Go to the [ngrok dashboard](https://dashboard.ngrok.com/signup) and create a free account.
2.  **Download**: Download the ngrok client for Linux.
3.  **Unzip**: Open a terminal and unzip the downloaded file:
    ```bash
    unzip /path/to/ngrok-v3-stable-linux-arm64.zip
    ```
4.  **Add Authtoken**: Connect your ngrok agent to your account. Copy the authtoken from your ngrok dashboard and run this command (replace `<YOUR_AUTHTOKEN>` with your actual token):
    ```bash
    ./ngrok config add-authtoken <YOUR_AUTHTOKEN>
    ```

**Step 2: Start the Secure Tunnel**

1.  **Run the NinjaRobot Web Server**: First, make sure your robot's web server is running. The default port is `8000`.
    ```bash
    uv run web-server
    ```
2.  **Start ngrok**: In a **new terminal window**, start ngrok to expose your local port `8000`.
    ```bash
    ./ngrok http 8000
    ```
3.  **Get Your HTTPS URL**: ngrok will display a "Forwarding" URL that looks something like this:
    `https://<random-string>.ngrok-free.app`

    Use this `https://` URL in your browser to access the robot's control panel. The microphone button for voice input will now be enabled.

(Example Interactions remain the same)

#### Other Interactive Utilities

(Other utility sections remain the same)
