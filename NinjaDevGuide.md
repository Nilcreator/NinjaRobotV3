# NinjaRobotV3 Development Guide

(Sections 1-4.4 remain the same)

### 4.5 Web Control Server

(Web Server introduction remains the same)

#### AI Agent Integration

The web server features a conversational AI agent powered by Google's Gemini model, supporting both text and voice.

**Backend Architecture (`ninja_agent.py` and `web_server.py`)**

1.  **`NinjaAgent` Class**: The agent class now contains two distinct methods for interaction:
    - `process_command()`: A non-streaming method that handles a single text-based request/response cycle. It supports function calling for web search.
    - `stream_conversation()`: An async generator designed to handle a real-time, bidirectional audio stream (currently simulated).

2.  **Dual Interaction Paths**:
    - **Text (HTTP)**: The `POST /api/agent/chat` endpoint handles text-based commands. It uses the `agent.process_command()` method and is a standard HTTP request-response.
    - **Voice (WebSocket)**: The `/ws/voice` endpoint is dedicated to handling streaming voice. It uses `agent.stream_conversation()` and manages a complex three-task asyncio structure to pass audio from the client to the agent and stream responses back.

3.  **Web Search**: Function calling is implemented in the `process_command` method, allowing the agent to use a `web_search` tool when it needs external information.

**Troubleshooting**\n\n-   **API Function Call Errors**: When sending a function response back to the Gemini model (e.g., after a web search), `ImportError` or `AttributeError` related to the `Part` class may occur. This is often due to version differences in the `google-generativeai` library. The most robust solution is to avoid importing `Part` directly and instead construct the response using a plain dictionary, which is less sensitive to library updates:\n    ```python\n    content={\"parts\": [{\"function_response\": {\"name\": \"web_search\", \"response\": {\...}}}]}\n    ```\n\n-   **JSON Parsing Errors**: The AI model may occasionally return responses that are not perfectly valid JSON (e.g., using single quotes), causing parsing errors. The current solution is to use a strict system prompt that explicitly instructs the model to return valid, double-quoted JSON.\n\n**Automated Secure Tunneling**: The web server (`web_server.py`) now automatically manages an `ngrok` subprocess to create a secure `https://` tunnel at startup. It fetches the public URL from the ngrok API and displays it in the console, removing the need for manual setup. The process is terminated automatically on server shutdown.

-   **Voice Agent Status (Diagnostic)**: The `stream_conversation` method in `ninja_agent.py` has been updated to be a diagnostic tool. Due to limitations in the `google-generativeai` library's support for bidirectional audio streaming, the agent currently consumes the audio stream and logs the receipt of data chunks, but does not yet process them. This confirms the frontend-to-backend connection is working and provides a basis for a future speech-to-text implementation.

**Frontend Architecture (`index.html` and `main.js`)**

1.  **HTTPS Requirement**: For voice input, the frontend now checks if the page is on a secure `https://` connection and alerts the user if it is not, as microphone access is blocked by browsers on insecure origins.

2.  **Interaction Flow**:
    - **Text Input**: The "Send" button triggers the `handleChatSend()` function, which makes a `fetch` call to the `POST /api/agent/chat` endpoint.
    - **Voice Input**: The microphone button now toggles recording. When clicked to stop, the `onstop` event of the `MediaRecorder` fires, sending the complete recorded audio as a single blob to the `/ws/voice` WebSocket.