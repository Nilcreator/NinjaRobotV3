# NinjaRobotV3 Development Guide

(Sections 1-4.4 remain the same)

### 4.5 Web Control Server

(Web Server introduction remains the same)

#### AI Agent Integration

The web server features a conversational AI agent powered by Google's Gemini model, supporting text-based commands.

**Backend Architecture (`ninja_agent.py` and `web_server.py`)**

1.  **`NinjaAgent` Class**: The agent class contains the `process_command()` method to handle a single text-based request/response cycle. It supports function calling for web search.

2.  **Interaction Path**: The `POST /api/agent/chat` endpoint handles all text-based commands. It uses the `agent.process_command()` method and is a standard HTTP request-response.

3.  **Web Search**: Function calling is implemented in the `process_command` method, allowing the agent to use a `web_search` tool when it needs external information.

**Troubleshooting**

-   **API Function Call Errors**: When sending a function response back to the Gemini model (e.g., after a web search), `ImportError` or `AttributeError` related to the `Part` class may occur. This is often due to version differences in the `google-generativeai` library. The most robust solution is to avoid importing `Part` directly and instead construct the response using a plain dictionary, which is less sensitive to library updates:
    ```python
    content={"parts": [{"function_response": {"name": "web_search", "response": {"...": "..."}}}]}
    ```

-   **JSON Parsing Errors**: The AI model may occasionally return responses that are not perfectly valid JSON (e.g., using single quotes), causing parsing errors. The current solution is to use a strict system prompt that explicitly instructs the model to return valid, double-quoted JSON.

**Automated Secure Tunneling (Optional)**: The web server (`web_server.py`) uses the `pyngrok` library to manage an `ngrok` secure tunnel. While no longer required for the core text-based functionality, this is preserved to provide a stable, secure HTTPS endpoint for accessing the web UI from outside the local network. `pyngrok` handles the entire lifecycle of the `ngrok` process. The `pi0ninja_v3` module includes `pyngrok` as a dependency.

**Frontend Architecture (`index.html` and `main.js`)**

-   **Interaction Flow**: The "Send" button triggers the `handleChatSend()` function, which makes a `fetch` call to the `POST /api/agent/chat` endpoint to send the user's text to the AI agent.
