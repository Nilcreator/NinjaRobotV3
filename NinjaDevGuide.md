# NinjaRobotV3 Development Guide

(Sections 1-4.4 remain the same)

### 4.5 Web Control Server

(Web Server introduction remains the same)

#### AI Agent Integration

The web server features a conversational AI agent powered by Google's Gemini model, supporting text-based commands.

**Backend Architecture (`ninja_agent.py` and `web_server.py`)**

1.  **`NinjaAgent` Class**:
    *   `process_command()`: Handles text-based request/response cycles and supports web search via function calling.
    *   `process_audio_command()`: Handles voice-based commands. It receives a path to an audio file, uploads it to the Gemini API for transcription and intent recognition, and processes the model's response.

2.  **Interaction Paths**:
    *   `POST /api/agent/chat`: Handles all text-based commands.
    *   `POST /api/agent/chat_voice`: Handles voice commands. It accepts a `multipart/form-data` request containing the audio file, saves it temporarily, and passes the file path to the agent's `process_audio_command()` method.

3.  **Web Search**: Function calling is implemented in the `process_command` method, allowing the agent to use a `web_search` tool when it needs external information.

**Troubleshooting**

-   **Gemini API File Upload Failures**: If an uploaded file's state becomes `FAILED`, it's likely because the API could not determine the file's type. This can be resolved by explicitly providing the `mime_type` when calling `genai.upload_file()`. For example, for the audio recorded by the web UI, use `mime_type="audio/webm"`.

-   **Gemini API File State Errors**: When uploading a file (e.g., for voice commands), the API may return a `400 Bad Request` with the error "File is not in an ACTIVE state." This is a timing issue. It occurs if you attempt to use the file in a `generate_content` call before the API has finished processing it. The solution is to poll the file's status after uploading. Use `genai.get_file()` in a loop with a delay (`time.sleep`) until `file.state.name` is `ACTIVE` before proceeding.

-   **API Function Call Errors**: When sending a function response back to the Gemini model (e.g., after a web search), `ImportError` or `AttributeError` related to the `Part` class may occur. This is often due to version differences in the `google-generativeai` library. The most robust solution is to avoid importing `Part` directly and instead construct the response using a plain dictionary, which is less sensitive to library updates:
    ```python
    content={"parts": [{"function_response": {"name": "web_search", "response": {"...": "..."}}}]}
    ```

-   **JSON Parsing Errors**: The AI model may occasionally return responses that are not perfectly valid JSON (e.g., using single quotes), causing parsing errors. The current solution is to use a strict system prompt that explicitly instructs the model to return valid, double-quoted JSON.

**Display Animation Architecture**: To solve LCD corruption issues ("noise"), the `AnimatedFaces` class was refactored to be fully thread-safe. It now internally manages a single `threading.Thread` for its animation loop. A new `_start_animation` method ensures that any active animation thread is properly stopped and joined before a new one begins, preventing multiple threads from accessing the SPI bus simultaneously. The `web_server.py` code was simplified to call the `play_*` methods of this class via `asyncio.to_thread`, offloading all complex thread management and cancellation logic to the `AnimatedFaces` class itself. This has fixed the race condition and stabilized the display.

**Servo Initialization**: The `ServoController` in `movement_recorder.py` has been updated to move all servos to their center position upon initialization. This resolves a `pigpio` warning and bug where the servo's state could not be read before it was first moved, leading to jerky initial movements.

**Frontend Architecture (`index.html` and `main.js`)**

-   **Text Interaction**: The "Send" button triggers the `handleChatSend()` function, which makes a `fetch` call to the `POST /api/agent/chat` endpoint.

-   **Voice Interaction**:
    *   A microphone button has been added to the UI.
    *   Clicking the button uses the `MediaRecorder` API to record audio from the user's microphone.
    *   The `AnalyserNode` from the Web Audio API is used to detect silence (pauses in speech). The recording automatically stops after 3 seconds of silence or a max duration of 30 seconds.
    *   The recorded audio `Blob` is sent as `FormData` to the `POST /api/agent/chat_voice` endpoint.
