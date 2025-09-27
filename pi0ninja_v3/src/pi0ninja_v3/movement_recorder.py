import json
import os
import time
import pigpio
import sys
import select
import termios
import tty
import copy
from piservo0.core.calibrable_servo import CalibrableServo

# Define file paths based on the script's location
NINJA_ROBOT_V3_ROOT = "/home/rogerchang/NinjaRobotV3"
SERVO_CONFIG_FILE = os.path.join(NINJA_ROBOT_V3_ROOT, "servo.json")
MOVEMENTS_FILE = os.path.join(NINJA_ROBOT_V3_ROOT, "servo_movement.json")

class ServoController:
    """A custom controller to manage multiple servos based on servo.json."""
    def __init__(self):
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise IOError("Failed to connect to pigpiod.")
        
        self.servos = {}
        self.servo_definitions = {}
        self._initialize_servos()

    def _initialize_servos(self):
        """Loads servo definitions, initializes CalibrableServo objects, and centers them."""
        try:
            with open(SERVO_CONFIG_FILE, 'r') as f:
                servo_configs = json.load(f)
            
            print("Initializing and centering servos...")
            for config in servo_configs:
                pin = config['pin']
                servo = CalibrableServo(
                    self.pi,
                    pin,
                    conf_file=SERVO_CONFIG_FILE
                )
                self.servos[pin] = servo
                self.servo_definitions[pin] = config
                
                # Set initial position to center to activate the servo
                servo.move_center()
                print(f"Initialized and centered servo on pin {pin}")
            
            # Give servos time to reach the center position
            time.sleep(0.5)
            print("All servos centered.")

        except FileNotFoundError:
            raise RuntimeError(f"Error: {SERVO_CONFIG_FILE} not found.")
        except Exception as e:
            raise RuntimeError(f"Error initializing servos: {e}")

    def get_servo_definitions(self):
        """Returns the raw servo definitions from the JSON file."""
        return self.servo_definitions

    def move_servos(self, movements, speed='M'):
        """
        Executes a set of servo movements with smooth interpolation.
        The duration of the movement is determined by the 'speed' parameter.
        """
        duration_map = {'S': 1.0, 'M': 0.5, 'F': 0.2}
        duration = duration_map.get(speed, 0.5)

        # Get current and target angles for interpolation
        pins_to_move = [int(p) for p in movements.keys()]
        current_angles = {p: self.servos[p].get_angle() for p in pins_to_move if p in self.servos}
        target_angles = {int(p): a for p, a in movements.items()}

        steps = int(duration / 0.02)  # 50 FPS update rate
        if steps <= 0:
            steps = 1

        for i in range(1, steps + 1):
            ratio = i / steps
            for pin in pins_to_move:
                if pin in self.servos:
                    start_angle = current_angles.get(pin, 0)
                    end_angle = target_angles.get(pin, 0)
                    
                    new_angle = start_angle + (end_angle - start_angle) * ratio
                    self.servos[pin].move_angle(new_angle)
            time.sleep(0.02)

        # Ensure final position is set accurately
        for pin in pins_to_move:
            if pin in self.servos:
                self.servos[pin].move_angle(target_angles.get(pin, 0))

    def get_current_angles(self):
        """Returns a dictionary of {pin: current_angle}."""
        return {pin: servo.get_angle() for pin, servo in self.servos.items()}

    def center_all_servos(self):
        """Moves all servos to their center position."""
        print("Centering all servos...")
        for servo in self.servos.values():
            servo.move_center()
        time.sleep(0.5)

    def cleanup(self):
        """Turns off all servos and disconnects from pigpio."""
        print("Cleaning up resources.")
        for servo in self.servos.values():
            servo.off()
        self.pi.stop()

def load_movements():
    """Loads movement sequences from the JSON file."""
    if not os.path.exists(MOVEMENTS_FILE):
        return {}
    try:
        with open(MOVEMENTS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_movements(movements):
    """Saves movement sequences to the JSON file."""
    with open(MOVEMENTS_FILE, 'w') as f:
        json.dump(movements, f, indent=4)

def parse_movement_command(command_str, definitions):
    """
    Parses the user's command string (e.g., 'S_17:30/27:M').
    Returns a tuple: (speed, {pin: angle_value}).
    """
    speed = 'M' # Default to Medium speed
    if command_str.startswith(('S_', 'M_', 'F_')):
        speed = command_str[0]
        command_str = command_str[2:]

    movements = {}
    parts = command_str.split('/')
    for part in parts:
        try:
            pin_str, angle_char = part.split(':')
            pin = int(pin_str)
            if pin not in definitions:
                raise ValueError(f"Servo pin {pin} is not defined in {SERVO_CONFIG_FILE}")

            angle = 0
            if angle_char.upper() == 'X':
                # Estimate max angle as 90
                angle = 90
            elif angle_char.upper() == 'M':
                # Estimate min angle as -90
                angle = -90
            elif angle_char.upper() == 'C':
                angle = 0
            else:
                angle = int(angle_char)
                if not -90 <= angle <= 90:
                    raise ValueError("Angle must be between -90 and 90.")
            
            movements[pin] = angle
        except ValueError as e:
            print(f"Error parsing '{part}': {e}")
            return None, None
            
    return speed, movements

def record_new_movement(controller):
    """Handles the UI and logic for recording a new movement sequence."""
    print("\n--- Record New Movement ---")
    print("Enter commands like '17:30/27:M' or 'S_22:-45'.")
    
    servo_defs = controller.get_servo_definitions()
    print("Available Servos (Pin, Min, Center, Max):")
    for pin, deets in servo_defs.items():
        print(f"  - Pin {pin}: Min={deets['min']}, Center={deets['center']}, Max={deets['max']}")

    # Start from a known, centered state
    print("\nSetting all servos to center position to begin...")
    controller.center_all_servos()

    sequence = []
    previous_angles = controller.get_current_angles()

    while True:
        command_str = input("Enter servo movement command: ").strip()
        if not command_str:
            continue

        speed, moves = parse_movement_command(command_str, servo_defs)
        if not moves:
            continue # Error message was already printed by the parser

        # --- Auto-complete with previous values for unmentioned servos ---
        all_servo_pins = servo_defs.keys()
        completed_moves = moves.copy()

        for pin in all_servo_pins:
            if pin not in completed_moves:
                # If a servo isn't in the command, use its last known angle
                previous_angle = previous_angles.get(pin, 0) # Default to center (0)
                completed_moves[pin] = previous_angle
        # --- End of auto-completion ---

        print(f"Executing full movement: {completed_moves} with speed {speed}")
        controller.move_servos(completed_moves, speed)
        
        while True:
            choice = input("1. Confirm & Next | 2. Reset | 3. Finish Recording: ").strip()
            if choice == '1':
                # Save the completed move set
                sequence.append({"speed": speed, "moves": completed_moves})
                previous_angles = controller.get_current_angles()
                print("Movement step confirmed.")
                break
            elif choice == '2':
                if not sequence:
                    print("Resetting to initial center position...")
                else:
                    print("Resetting to previous position...")
                # Revert all servos to the last known good state
                controller.move_servos(previous_angles, 'F') # Reset quickly
                break # Goes back to re-input the command
            elif choice == '3':
                # Save the last move before finishing
                sequence.append({"speed": speed, "moves": completed_moves})
                print("Last movement step confirmed.")

                if not sequence:
                    print("No movements recorded. Aborting.")
                    return

                movement_name = input("Enter a name for this movement: ").strip()
                if not movement_name:
                    print("Name cannot be empty. Aborting save.")
                    # If save is aborted, return servos to a neutral state
                    controller.center_all_servos()
                    return
                
                all_movements = load_movements()
                all_movements[movement_name] = sequence
                save_movements(all_movements)
                print(f"Movement '{movement_name}' saved!")
                controller.center_all_servos()
                return
            else:
                print("Invalid option.")

class NonBlockingKeyboard:
    """A class to handle non-blocking keyboard input."""
    def __enter__(self):
        self.old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        return self

    def __exit__(self, type, value, traceback):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

    def kbhit(self):
        """Check if a key has been pressed."""
        return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

    def getch(self):
        """Get the pressed character."""
        return sys.stdin.read(1)

def execute_movement(controller):
    """Handles the UI and logic for executing a saved movement with looping and interruption."""
    print("\n--- Execute a Movement ---")
    all_movements = load_movements()
    if not all_movements:
        print("No movements have been recorded yet.")
        return

    print("Select a movement to execute:")
    names = list(all_movements.keys())
    for i, name in enumerate(names):
        print(f"{i + 1}. {name}")

    try:
        choice = int(input("Enter number: ")) - 1
        if not 0 <= choice < len(names):
            raise ValueError()
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    loop_input = input("Enter the number of times to loop, or 'loop' for infinite: ").strip().lower()
    
    loop_count = 0
    infinite_loop = False
    if loop_input == 'loop':
        infinite_loop = True
    else:
        try:
            loop_count = int(loop_input)
            if loop_count <= 0:
                print("Loop count must be a positive integer.")
                return
        except ValueError:
            print("Invalid input for loop count.")
            return

    selected_name = names[choice]
    sequence = all_movements[selected_name]
    
    print(f"Executing movement: '{selected_name}'...")
    print("Press Enter or Esc to interrupt.")
    controller.center_all_servos()
    
    interrupted = False
    with NonBlockingKeyboard() as nkb:
        loops_done = 0
        while infinite_loop or loops_done < loop_count:
            for i, step in enumerate(sequence):
                if nkb.kbhit():
                    key = nkb.getch()
                    if key == '\r' or key == '\x1b': # Enter or Esc
                        interrupted = True
                        break
                
                print(f"  - Loop {loops_done + 1}, Step {i+1}: {step['moves']}")
                controller.move_servos(step['moves'], step['speed'])
            
            if interrupted:
                break
            loops_done += 1

    if interrupted:
        print("\nMovement interrupted by user.")
    else:
        print("\nMovement '{selected_name}' finished.")
    
    time.sleep(1)
    controller.center_all_servos()

def edit_sequence_menu(controller, sequence_to_edit):
    """UI for editing a sequence. Operates on a copy and returns it if saved."""
    temp_sequence = copy.deepcopy(sequence_to_edit)
    servo_defs = controller.get_servo_definitions()

    try:
        while True:
            print("\n--- Editing Sequence ---")
            for i, step in enumerate(temp_sequence):
                print(f"Step {i + 1}: Speed={step['speed']}, Moves={step['moves']}")

            print("\nOptions:")
            print("1. Edit a step")
            print("2. Insert a new step")
            print("3. Delete a step")
            print("4. Preview the sequence")
            print("5. Finish and Save")
            print("6. Abort without saving")
            
            edit_choice = input("Select an option: ").strip()

            if edit_choice == '1': # Edit a step
                try:
                    step_num = int(input("Enter step number to edit: ")) - 1
                    if not 0 <= step_num < len(temp_sequence):
                        raise ValueError()
                    
                    print(f"Current step: {temp_sequence[step_num]}")
                    command_str = input("Enter new movement command (e.g., 'S_17:30/27:C'): ").strip()
                    speed, moves = parse_movement_command(command_str, servo_defs)
                    
                    if moves:
                        # Auto-complete the move
                        completed_moves = moves.copy()
                        all_servo_pins = servo_defs.keys()
                        base_angles = temp_sequence[step_num - 1]['moves'] if step_num > 0 else controller.get_current_angles()
                        for pin in all_servo_pins:
                            if pin not in completed_moves:
                                completed_moves[pin] = base_angles.get(pin, 0)
                        
                        temp_sequence[step_num] = {"speed": speed, "moves": completed_moves}
                        print("Step updated.")

                except (ValueError, IndexError):
                    print("Invalid step number.")

            elif edit_choice == '2': # Insert a new step
                try:
                    step_num = int(input(f"Enter position to insert new step (1 to {len(temp_sequence) + 1}): ")) - 1
                    if not 0 <= step_num <= len(temp_sequence):
                        raise ValueError()

                    command_str = input("Enter movement command for the new step: ").strip()
                    speed, moves = parse_movement_command(command_str, servo_defs)

                    if moves:
                        # Auto-complete the move
                        completed_moves = moves.copy()
                        all_servo_pins = servo_defs.keys()
                        base_angles = temp_sequence[step_num - 1]['moves'] if step_num > 0 else controller.get_current_angles()
                        for pin in all_servo_pins:
                            if pin not in completed_moves:
                                completed_moves[pin] = base_angles.get(pin, 0)

                        temp_sequence.insert(step_num, {"speed": speed, "moves": completed_moves})
                        print("Step inserted.")

                except (ValueError, IndexError):
                    print("Invalid position.")

            elif edit_choice == '3': # Delete a step
                try:
                    step_num = int(input("Enter step number to delete: ")) - 1
                    if not 0 <= step_num < len(temp_sequence):
                        raise ValueError()
                    
                    confirm = input(f"Delete Step {step_num + 1}? (y/n): ").lower()
                    if confirm == 'y':
                        del temp_sequence[step_num]
                        print("Step deleted.")
                except (ValueError, IndexError):
                    print("Invalid step number.")
            elif edit_choice == '4': # Preview
                print("Previewing sequence...")
                controller.center_all_servos()
                for i, step in enumerate(temp_sequence):
                    print(f"  - Step {i+1}: {step['moves']}")
                    controller.move_servos(step['moves'], step['speed'])
                print("Preview finished.")
                time.sleep(1)
                controller.center_all_servos()
            elif edit_choice == '5': # Finish and Save
                print("Finishing and saving changes.")
                return temp_sequence
            elif edit_choice == '6': # Abort
                print("Aborting without saving.")
                return None
            else:
                print("Invalid option.")

    except KeyboardInterrupt:
        print("\nModification cancelled. No changes were saved.")
        return None

def modify_existing_movement(controller):
    """Handles the non-destructive modification of a movement sequence."""
    print("\n--- Modify Existing Movement ---")
    all_movements = load_movements()
    if not all_movements:
        print("No movements have been recorded yet.")
        return

    print("Select a movement to modify:")
    names = list(all_movements.keys())
    for i, name in enumerate(names):
        print(f"{i + 1}. {name}")

    try:
        choice = int(input("Enter number: ")) - 1
        if not 0 <= choice < len(names):
            raise ValueError()
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    selected_name = names[choice]
    original_sequence = all_movements[selected_name]

    print(f"\nLoading '{selected_name}' into the editor.")
    
    # The edit_sequence_menu function will handle the safe editing
    modified_sequence = edit_sequence_menu(controller, original_sequence)

    if modified_sequence is not None:
        # If the user saved, overwrite the original sequence and save to file
        all_movements[selected_name] = modified_sequence
        save_movements(all_movements)
        print(f"Successfully saved changes to '{selected_name}'.")
    else:
        # If the user aborted or interrupted, no changes are made
        print(f"No changes were made to '{selected_name}'.")

def clear_movement(controller):
    """Handles the UI and logic for clearing a movement sequence."""
    print("\n--- Clear Movement ---")
    all_movements = load_movements()
    if not all_movements:
        print("No movements have been recorded yet.")
        return

    print("Select a movement to clear:")
    names = list(all_movements.keys())
    for i, name in enumerate(names):
        print(f"{i + 1}. {name}")

    try:
        choice = int(input("Enter number: ")) - 1
        if not 0 <= choice < len(names):
            raise ValueError()
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    selected_name = names[choice]
    confirm = input(f"Are you sure you want to delete '{selected_name}'? (y/n): ").lower()
    if confirm == 'y':
        del all_movements[selected_name]
        save_movements(all_movements)
        print(f"Movement '{selected_name}' has been deleted.")
    else:
        print("Deletion cancelled.")

def main_menu():
    """Displays the main menu and handles user selection."""
    controller = ServoController()
    
    try:
        while True:
            print("\n--- Servo Movement Recorder ---")
            print("1. Record new movement")
            print("2. Modify existing movement")
            print("3. Execute a movement")
            print("4. Clear movement")
            print("5. Exit")
            choice = input("Select an option: ")

            if choice == '1':
                record_new_movement(controller)
            elif choice == '2':
                modify_existing_movement(controller)
            elif choice == '3':
                execute_movement(controller)
            elif choice == '4':
                clear_movement(controller)
            elif choice == '5':
                break
            else:
                print("Invalid choice. Please try again.")
    finally:
        controller.cleanup()

if __name__ == "__main__":
    main_menu()
