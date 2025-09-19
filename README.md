# NinjaRobot Development Log

This file tracks the development progress of the NinjaRobot project.

## Environment Setup

To ensure all robot components and drivers are correctly installed and accessible, run the following command from the root directory (`NinjaRobotV3/`):

```bash
uv pip install -e ./pi0ninja_v3 -e ./piservo0 -e ./pi0disp -e ./vl53l0x_pigpio -e ./pi0buzzer
```

This installs all necessary local packages in editable mode.

## Development History

### 2025-09-19: Facial Expression Viewer

- **New Utility:** Created the `show_faces.py` script, an interactive tool for previewing all facial expressions on the robot's display.
- **Persistent Idle State:** The tool features a continuous, non-blocking idle animation with random blinks, which serves as the robot's default state.
- **Interactive Menu:** Users can press `m` to pause the idle animation and open a menu to select and display other expressions for a fixed duration.
- **Robust Architecture:** Refactored the script to use a non-blocking main loop for the idle state and a standard blocking menu for selection. This avoids using `KeyboardInterrupt` for control flow and prevents display corruption bugs.

### 2025-09-18: Documentation Overhaul

- **Comprehensive User Guide:** Completely rewrote the `Servo Movement Recorder` section in `NinjaUserGuide.md`. The new guide provides detailed, user-friendly instructions for all the latest features, including the non-destructive modification workflow, looping/interruptible playback, and improved recording process.
- **Developer Guide Update:** Added a new section to `NinjaRobot_DevGuide.md` describing the `movement_recorder` tool, its purpose as a high-level utility, and its role as an integration example for the `piservo0` library.
- **Centralized Logging:** Consolidated all recent feature enhancements under a new development log entry to reflect the current state of the project accurately.


### 2025-09-12: Facial Expression System

- **Project Initialization:** Created the `pi0ninja_v3` library to house the robot's core logic and established this `README.md` for progress tracking.

- **Animation Library:** Developed `facial_expressions.py`, a library for generating 14 unique, programmatically drawn and animated facial expressions (e.g., Idle, Happy, Sad).

- **Integration & Testing:** Integrated the animation library into the main control script (`main_robot_control.py`) to cycle through all expressions on startup.

- **Dependency Management:** Resolved `ModuleNotFoundError` and `TOML` configuration errors by correctly installing all local driver packages (`pi0disp`, `piservo0`, etc.) into the project's virtual environment.

- **Visual Refinement & Bug Fixes:** Iteratively improved the facial animations by:
    - Centering and scaling all expressions.
    - Unifying the visual style based on a design reference (`angry.jpg`).
    - Increasing the animation framerate to ~60 FPS.
    - Correcting visual bugs where features were overlapping or disappearing.

### 2025-09-17: Servo Movement Recorder

- **Movement Recording Tool:** Developed `movement_recorder.py`, a CLI tool for creating, modifying, and deleting named servo movement sequences.
- **Core Functionality:**
    - **Record:** Interactively command servos to specific angles (`-90` to `90`, plus `X` for max, `M` for min, `C` for center) and save the sequence of movements. The final movement is now automatically saved when you finish recording. Supports speed control (`S_` for slow).
    - **Modify:** A safe, non-destructive editor for fine-tuning movement sequences.
        - **Transactional Editing:** Changes are made to a temporary copy. The original movement is not altered unless you explicitly save.
        - **Graceful Interruption:** Exiting with `Ctrl+C` will safely discard all changes.
        - **Granular Control:** You can edit, insert, or delete specific steps within the sequence.
        - **Preview:** Play back the modified sequence before saving to ensure it's correct.
    - **Clear:** Delete a saved movement sequence.
- **Servo Abstraction:** Implemented a `ServoController` class to manage multiple servos using the `piservo0` library, loading configurations from `servo.json`.
- **Data Persistence:** All named movement sequences are saved to `servo_movement.json` in the project root.
- **Usage:** The tool can be run directly from the command line:
  ```bash
  uv run python -m pi0ninja_v3.movement_recorder
  ```
- **Recording Optimization:** Enhanced the recording process to automatically capture the state of all servos for every step. If a servo is not explicitly commanded, its previous position is automatically carried over, ensuring every step in the saved sequence is a complete keyframe.
- **Execution with Looping and Interruption:**
    - When executing a movement, you can now specify a number of times to loop the sequence or enter 'loop' for infinite playback.
    - Movement playback can be interrupted at any time by pressing the `Enter` or `Esc` key.
