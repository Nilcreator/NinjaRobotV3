import sys
from PIL import ImageDraw
import select
import termios
import tty
import inspect
import time
import random
from pi0disp.disp.st7789v import ST7789V
from pi0ninja_v3.facial_expressions import AnimatedFaces

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

def get_face_methods(animated_faces_instance):
    """Inspects the AnimatedFaces instance and returns a dictionary of face-playing methods."""
    face_methods = {}
    for name, method in inspect.getmembers(animated_faces_instance, predicate=inspect.ismethod):
        if name.startswith('play_'):
            clean_name = name.replace('play_', '')
            face_methods[clean_name] = method
    return face_methods

def draw_idle_frame(faces, is_blinking):
    """Draws a single frame of the idle animation."""
    image = faces._get_blank_image()
    draw = ImageDraw.Draw(image)
    if is_blinking:
        draw.line([faces.center_x - faces.eye_offset - 30, faces.eye_y, faces.center_x - faces.eye_offset + 30, faces.eye_y], fill=faces.face_color, width=faces.line_width)
        draw.line([faces.center_x + faces.eye_offset - 30, faces.eye_y, faces.center_x + faces.eye_offset + 30, faces.eye_y], fill=faces.face_color, width=faces.line_width)
    else:
        faces._draw_base_eyes(draw)
    draw.arc([faces.center_x - 50, faces.mouth_y - 10, faces.center_x + 50, faces.mouth_y + 10], 0, 180, fill=faces.face_color)
    faces.lcd.display(image)

def main():
    """Main function with a non-blocking idle loop and a blocking menu."""
    try:
        with ST7789V() as lcd:
            faces = AnimatedFaces(lcd)
            face_options = get_face_methods(faces)
            option_list = list(face_options.keys())

            # --- Idle Animation State ---
            next_blink_time = time.time() + random.uniform(5, 15)
            blink_duration = 0.15
            is_blinking = False
            blink_start_time = 0

            print("Starting idle animation. Press 'm' for menu, 'q' to quit.")

            with NonBlockingKeyboard() as nkb:
                while True:
                    # --- Non-blocking keyboard check ---
                    if nkb.kbhit():
                        key = nkb.getch()
                        if key == 'q':
                            print("\nExiting...")
                            break
                        if key == 'm':
                            # --- Blocking Menu Interaction ---
                            print("\n--- Select a Facial Expression ---")
                            for i, name in enumerate(option_list):
                                print(f"{i + 1}. {name}")
                            print("\nEnter a number to display the face, or any other key to return to idle.")
                            
                            # Temporarily exit non-blocking mode for standard input
                            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, nkb.old_settings)
                            choice = input("Your choice: ").strip().lower()
                            # Re-enter non-blocking mode
                            tty.setcbreak(sys.stdin.fileno())

                            try:
                                choice_index = int(choice) - 1
                                if 0 <= choice_index < len(option_list):
                                    selected_face_name = option_list[choice_index]
                                    print(f"\nDisplaying: {selected_face_name}")
                                    face_options[selected_face_name](duration_s=5)
                                    print("Returning to idle. Press 'm' for menu, 'q' to quit.")
                                    # Reset blink timer after animation
                                    next_blink_time = time.time() + random.uniform(5, 15)
                                else:
                                    print("Invalid number. Returning to idle.")
                            except ValueError:
                                print("Invalid input. Returning to idle.")
                            continue # Restart loop to get fresh screen

                    # --- Idle Animation Logic ---
                    current_time = time.time()

                    if not is_blinking and current_time >= next_blink_time:
                        is_blinking = True
                        blink_start_time = current_time

                    if is_blinking:
                        if current_time >= blink_start_time + blink_duration:
                            is_blinking = False
                            next_blink_time = current_time + random.uniform(5, 15)
                    
                    draw_idle_frame(faces, is_blinking)
                    time.sleep(1/60) # ~60 FPS

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()