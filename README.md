# NinjaRobot Development Log

This file tracks the development progress of the NinjaRobot project.

## Environment Setup

To ensure all robot components and drivers are correctly installed and accessible, run the following command from the root directory (`NinjaRobotV3/`):

```bash
uv pip install -e ./pi0ninja_v3 -e ./piservo0 -e ./pi0disp -e ./vl53l0x_pigpio -e ./pi0buzzer
```

This installs all necessary local packages in editable mode.

## Development History

### 2025-09-27: Fixed Sound Playback Crash

- **Problem**: The application would crash with an `AttributeError` when the AI agent tried to play a sound, particularly after a voice command.
- **Root Cause**: A regression was introduced in a previous refactoring. The code was incorrectly calling the `RobotSoundPlayer.play` method as a static method and passing the wrong arguments, leading to the error.
- **Solution**: The sound playback logic in `web_server.py` was corrected. It now uses the available `buzzer` controller to correctly iterate through the sound's melody and play each note, resolving the crash.

### 2025-09-27: Refactored Display Logic for Thread-Safety

- **Problem**: The LCD screen displayed corrupted data ("noise") when changing facial expressions, indicating a critical race condition.
- **Root Cause**: The `AnimatedFaces` class was not thread-safe. Multiple threads were being created by the web server to play different animations, and they were attempting to write to the SPI display simultaneously without any locking or coordination.
- **Solution**: The `AnimatedFaces` class in `facial_expressions.py` was completely refactored. It now manages its own internal `threading.Thread` and uses a `threading.Event` to ensure that only one animation can be active at a time. A new `_start_animation` method safely stops any existing animation thread before starting a new one, eliminating the race condition. The logic in `web_server.py` was then greatly simplified to rely on this new thread-safe class, removing the need for complex and faulty `asyncio.Task` management for the display.

### 2025-09-27: Display Task and Shutdown Reliability Fix

- **Problem**: The server would freeze on shutdown, and the LCD screen would show noise when changing facial expressions.
- **Root Cause**: The background display task was not being managed correctly, leading to an infinite loop blocking shutdown and race conditions causing screen corruption.
- **Solution**:
    - **Centralized Task Management**: Implemented a robust task management system for all display animations. A single, authoritative background task is now tracked in the application state. This task is properly cancelled and replaced when expressions change, eliminating race conditions.
    - **Graceful Shutdown**: The `lifespan` manager now explicitly cancels the display task on shutdown, allowing the server to terminate cleanly and fixing the freeze on Ctrl+C.
    - **Idle on Interaction**: The QR code is now displayed until the user sends their first command, at which point the screen transitions to a persistent idle face.

### 2025-09-27: Server Shutdown and Interaction Fixes

- **Problem**: The server would freeze on shutdown (Ctrl+C), and the display did not provide feedback when a user started interacting with the robot.
- **Root Cause**: The background display task was not being cancelled on shutdown, causing an infinite loop to block the process from exiting.
- **Solution**:
    - **Shutdown Fix**: Implemented proper background task management in the `lifespan` manager. The display task is now tracked and explicitly cancelled on shutdown, allowing the server to exit cleanly.
    - **Idle Face on Interaction**: The display now shows the QR code indefinitely until a user sends the first chat command. Upon this first interaction, the QR code is replaced by a persistent `idle` face animation, providing clear visual feedback that the robot is "awake".

### 2025-09-27: QR Code Display Fix and Startup Refinement

- **Problem**: The QR code display on the LCD screen was crashing the application due to an incorrect image format, and the startup sequence was not optimal.
- **Root Cause**: The QR code image was being generated in a grayscale format, which was incompatible with the display driver that expected an RGB image. 
- **Solution**:
    - Modified `web_server.py` to explicitly convert the QR code image to 'RGB' format before displaying it, fixing the crash.
    - Refactored the startup logic within the `lifespan` manager to ensure all hardware and agent initializations are logged before the network and display sequences begin, providing a clearer startup log for the user.

### 2025-09-27: Ngrok Connection Resiliency

- **Problem**: The `ngrok` service was failing to start due to network timeouts, preventing the web server from being accessible remotely.
- **Root Cause**: Transient network issues were causing the initial `ngrok.connect()` call to fail.
- **Solution**: Implemented a retry mechanism in `web_server.py`. The application now attempts to connect to the ngrok service up to 3 times with a 5-second delay between attempts, making the startup process more resilient to temporary network glitches.

### 2025-09-27: Startup and Servo Performance Optimization

- **Change**: Overhauled the web server startup sequence and fixed a critical servo initialization bug.
- **Reason**: To provide a better user experience on startup and to resolve servo performance issues.
- **Implementation**:
    - **Startup Sequence**: The `web_server.py` `lifespan` manager now orchestrates the entire startup. It starts `ngrok`, displays a QR code of the URL on the robot's LCD for 60 seconds, and then transitions the display to an `idle` face to show the robot is ready.
    - **Servo Fix**: Modified `movement_recorder.py` to move all servos to their center position upon initialization. This "activates" the servos with `pigpio`, eliminating `pigpio err` warnings and ensuring smooth movement from a known starting state.
- **Documentation**: Updated all relevant user and developer guides to reflect the new, more robust startup procedure and the servo performance fix.

### 2025-09-27: QR Code for Easy Access

- **Change**: The web server now generates a QR code of the secure `ngrok` URL and displays it on the robot's LCD screen upon startup.
- **Reason**: To provide a fast and convenient way for users to access the web control interface on a mobile device without having to manually type the URL.
- **Implementation**:
    - Added the `qrcode` library as a dependency.
    - Modified `web_server.py` to use the `qrcode` library to generate an image of the URL.
    - Integrated the `pi0disp` driver to display the generated QR code image on the ST7789V screen.
- **Documentation**: Updated the `InstallationGuide.md`, `NinjaUserGuide.md`, and `NinjaDevGuide.md` to reflect this new feature.

### 2025-09-23: Voice Input Upload Fix

- **Problem**: The voice input feature failed with an error indicating the uploaded file processing had `FAILED`.
- **Root Cause**: The Gemini API was rejecting the uploaded audio file because its type was not explicitly specified. Although the file was a standard `.webm`, the API requires the MIME type for reliable processing.
- **Solution**: Modified `ninja_agent.py` to explicitly set `mime_type="audio/webm"` in the `genai.upload_file()` call. This ensures the API correctly identifies and processes the audio file, resolving the upload failure.

### 2025-09-23: Voice Input Robustness Fix

- **Problem**: The voice input feature failed with a `400 Bad Request` error, stating the uploaded audio file was "not in an ACTIVE state."
- **Root Cause**: A timing issue where the application was sending the uploaded audio file to the Gemini model for processing before the API had finished preparing it.
- **Solution**: Implemented a robust waiting mechanism in `ninja_agent.py`. The code now uploads the file, then polls the Gemini API, waiting until the file's status is 'ACTIVE' before sending it to the model. This includes a timeout to prevent indefinite waiting and ensures the temporary file is deleted, resolving the error and making the voice feature reliable.

### 2025-09-23: Environment Sync Fix

- **Problem**: The web server failed to start with a `RuntimeError`, indicating the `python-multipart` dependency was not installed.
- **Root Cause**: The project's virtual environment was out of sync with the `pyproject.toml` file, which already specified the dependency correctly.
- **Solution**: Re-ran the `uv pip install` command to synchronize the environment and install the missing package. This resolves the startup error.

### 2025-09-23: Voice Input Feature Re-instated

- **Change**: A "record-then-process" voice input feature has been added to the web interface.
- **Reason**: To provide an alternative, hands-free method for sending commands to the robot, as requested. This implementation differs from the previous live streaming approach.
- **Implementation**:
    - **Frontend**: A microphone button was added. It uses the `MediaRecorder` and Web Audio APIs to record user speech, automatically stopping on silence (3s) or after a maximum duration (30s).
    - **Backend**: A new endpoint (`/api/agent/chat_voice`) accepts the recorded audio file. The `NinjaAgent` uses the Gemini API's multimodal capabilities to transcribe the audio and execute the command.
- **Linting**: Added `ruff` as a development dependency to `pi0ninja_v3` to ensure code quality for new backend changes.


### 2025-09-23: Voice Input Feature Removal

- **Change**: The live voice input feature has been completely removed from the project.
- **Reason**: To simplify the user interface and core functionality, focusing on the text-based chat experience.
- **Impact**:
    - The `ninja_agent` has been updated to only process text commands.
    - The `/ws/voice` WebSocket endpoint and all related backend code have been removed.
    - The microphone button and all associated JavaScript have been removed from the frontend.
    - All documentation has been updated to reflect the removal of this feature.
    - The `pyngrok` integration is preserved to provide a reliable, secure HTTPS tunnel to the web interface, but is no longer a requirement for the primary AI functionality.

### 2025-09-23: Architectural Change: Ngrok Integration Refactored to `pyngrok`

- **Problem**: The automated `ngrok` startup was unreliable, failing with `Connection refused` errors. The manual `subprocess` management approach was brittle and difficult to debug.
- **Root Cause**: The `subprocess` approach did not provide robust control over the `ngrok` process lifecycle, leading to race conditions and silent failures.
- **Solution**: Replaced the entire manual `subprocess` and `requests` implementation with the `pyngrok` library. This is a major architectural improvement that delegates all `ngrok` process management to a dedicated, robust library. `pyngrok` now handles the tunnel creation, URL fetching, and shutdown, resolving the startup failures and making the code cleaner and more reliable. The `pi0ninja_v3` dependencies and the web server startup sequence have been updated accordingly.

### 2025-09-22: Ngrok Automatic Startup Reliability Fix

- **Problem**: The automated `ngrok` secure tunnel failed to activate intermittently upon starting the web server.
- **Root Cause**: A race condition was identified where the server script attempted to fetch the public URL from the `ngrok` API before the `ngrok` service had fully initialized. The previous static `time.sleep()` was an unreliable solution.
- **Solution**: Replaced the fixed delay with a robust retry mechanism in the `get_ngrok_url` function. The function now repeatedly attempts to connect to the `ngrok` API for a few seconds, ensuring it only proceeds once the tunnel is active and the URL is available. This makes the automatic HTTPS startup process reliable.

### 2025-09-21: Voice Agent Re-architecture

- **Problem**: The voice agent was unresponsive because the underlying Gemini library does not support true bidirectional audio streaming. The previous implementation was only a diagnostic placeholder.
- **Solution**: Re-architected the entire voice pipeline to a "record-then-process" model. The frontend now records the user's full utterance and sends the complete audio file to the backend. The `NinjaAgent` was updated with a new `process_audio_input` method that sends the audio data directly to the Gemini API for transcription and execution. This provides a fully functional and reliable voice command experience.
- **UI**: The frontend was updated to provide clear visual feedback for "recording" and "processing" states.

### 2025-09-21: Automated HTTPS and Voice Agent Diagnostics

- **Ngrok Automation**: Modified the `web_server.py` script to automatically start, manage, and terminate an `ngrok` subprocess. The server now fetches and displays the public HTTPS URL on startup, streamlining the process of enabling the microphone for voice input.
- **Voice Agent Diagnostic**: Addressed an issue where the voice agent was unresponsive. The `ninja_agent.py` was updated to consume the audio stream and log the receipt of data, confirming the data pipeline is working. This serves as a diagnostic step while a full speech-to-text implementation is pending.

### 2025-09-21: HTTPS Voice Input and Linting

- **HTTPS for Voice Input**: Successfully configured and enabled `ngrok` to provide a secure HTTPS tunnel to the local web server. This resolves the browser security error (`Microphone access requires a secure (HTTPS) connection`) and enables the microphone for live voice interaction with the AI agent.
- **Code Linting**: Fixed several linting issues in the `pi0ninja_v3` codebase, including unused imports and module-level imports not being at the top of the file, improving code quality and adherence to standards.

### 2025-09-21: AI Agent Web Search Fix (ImportError)

- **Problem**: Fixed an `ImportError: cannot import name 'Part' from 'google.generativeai.types'` that occurred at startup.
- **Root Cause**: A previous fix for an `AttributeError` incorrectly assumed the `Part` class was available for import. The `ImportError` revealed that the installed version of the `google-generativeai` library does not expose this class in its `types` module.
- **Solution**: To create a more robust and version-agnostic solution, the code was refactored to not rely on importing the `Part` class. Instead, the function response is now constructed using a standard Python dictionary, which the library accepts. This resolves the import error and makes the code less likely to break with future library updates.

### 2025-09-21: AI Agent and Documentation Update

- **JSON Parsing Robustness**: Addressed a bug where the AI agent would fail to parse responses from the language model due to invalid JSON formatting (e.g., single quotes). The system prompt was enhanced to enforce a strict, double-quoted JSON output for all action commands. Diagnostic logging was also added to capture the raw AI response for easier debugging.
- **HTTPS for Voice Input**: Resolved the issue where voice input was disabled. This was identified as a browser security feature requiring an HTTPS connection. The `NinjaUserGuide.md` was updated with a comprehensive, step-by-step guide on how to use `ngrok` to create a secure `https://` tunnel for local development. The `NinjaDevGuide.md` was also updated to reflect these changes.

### 2025-09-21: AI Agent Bug Fix

- **Problem**: Fixed a `ModuleNotFoundError: No module named 'default_api'` that occurred when starting the web server.
- **Root Cause**: The error was caused by an incorrect import of a `google_web_search` function that was not defined. The agent was trying to import a tool as a regular module.
- **Solution**: Removed the incorrect import and implemented the `web_search` function within the `NinjaAgent` class using the `googlesearch-python` library. This resolves the startup crash and correctly integrates the web search tool with the agent's capabilities.

### 2025-09-21: AI Agent Major Upgrade

- **Live Voice Streaming**: Re-architected the AI agent to support real-time, low-latency voice conversations. The implementation now uses a WebSocket (`/ws/voice`) to stream audio directly from the browser to the backend, which then communicates with the Gemini streaming model. This replaces the previous text-based input and provides a much more natural and interactive experience.
- **Web Search Capability**: Integrated function calling into the AI agent. The agent can now decide when to search the web to answer questions beyond its core capabilities (e.g., weather, facts, news). It uses the `google_web_search` tool and incorporates the findings into its conversational responses.
- **Bug Fixes & Enhancements**:
    - Fixed a critical bug where the robot would not execute movements planned by the AI agent.
    - Improved the AI's system prompt to be more robust in understanding multilingual commands and intents.
    - Updated all relevant documentation (`README.md`, `NinjaUserGuide.md`, `NinjaDevGuide.md`) to reflect the new architecture and features.

### 2025-09-20: Web Server Usability

- **Enhanced Startup Message**: Improved the web server's startup sequence to automatically detect and display both the hostname and IP address connection URLs, making it easier for users to connect to the robot's control panel.

### 2025-09-20: Servo Driver Bug Fix

- **Problem**: Fixed a `pigpio.error: 'GPIO is not in use for servo pulses'` that occurred when executing a servo movement from the web interface for the first time.
- **Root Cause**: The error was caused by the system trying to read the.current position of a servo that had not yet been activated, resulting in an invalid state.
- **Solution**: Made the underlying `piservo0` driver more robust. The `get_pulse()` method was updated to catch the error and return a default center value, allowing movements to start correctly from a "cold" state.

(Previous entries remain)
