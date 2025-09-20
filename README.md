# NinjaRobot Development Log

This file tracks the development progress of the NinjaRobot project.

## Environment Setup

To ensure all robot components and drivers are correctly installed and accessible, run the following command from the root directory (`NinjaRobotV3/`):

```bash
uv pip install -e ./pi0ninja_v3 -e ./piservo0 -e ./pi0disp -e ./vl53l0x_pigpio -e ./pi0buzzer
```

This installs all necessary local packages in editable mode.

## Development History

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
