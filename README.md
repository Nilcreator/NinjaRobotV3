# NinjaRobot Development Log

This file tracks the development progress of the NinjaRobot project.

## Environment Setup

To ensure all robot components and drivers are correctly installed and accessible, run the following command from the root directory (`NinjaRobotV3/`):

```bash
uv pip install -e ./pi0ninja_v3 -e ./piservo0 -e ./pi0disp -e ./vl53l0x_pigpio -e ./pi0buzzer
```

This installs all necessary local packages in editable mode.

## Development History

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
