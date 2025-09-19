
import pigpio
import time
import json
import os
import sys

# Add the parent directory to the path to find the pi0buzzer library
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from pi0buzzer.driver import Buzzer

class RobotSoundPlayer:
    """
    A class to play sounds corresponding to robot emotions using a buzzer.
    """
    # Note mapping from pi0buzzer (C4-B6)
    NOTES = {
        'c4': 262, 'd4': 294, 'e4': 330, 'f4': 349, 'g4': 392, 'a4': 440, 'b4': 494,
        'c5': 523, 'd5': 587, 'e5': 659, 'f5': 698, 'g5': 784, 'a5': 880, 'b5': 988,
        'c6': 1046, 'd6': 1175, 'e6': 1318, 'f6': 1397, 'g6': 1568, 'a6': 1760, 'b6': 1976,
    }

    SOUNDS = {
        "happy": [('c5', 0.1), ('e5', 0.1), ('g5', 0.1), ('c6', 0.15)],
        "sad": [('b4', 0.4), ('a4', 0.4), ('g4', 0.6)],
        "exciting": [('c6', 0.08), ('e6', 0.08), ('g6', 0.08), ('c6', 0.08), ('e6', 0.08), ('g6', 0.08)],
        "angry": [('d4', 0.1), ('c4', 0.1), ('d4', 0.1), ('c4', 0.2)],
        "confusing": [('e5', 0.2), ('g4', 0.2), ('c5', 0.3)],
        "cry": [('e5', 0.3), ('d5', 0.2), ('c5', 0.5), ('pause', 0.2), ('c5', 0.4)],
        "embarrassing": [('a4', 0.15), ('g4', 0.15), ('a4', 0.3)],
        "idle": [('c5', 0.1), ('pause', 0.5), ('c5', 0.1)],
        "laughing": [('g5', 0.1), ('pause', 0.05)] * 5,
        "scary": [('c4', 0.5), ('d4', 0.2), ('c4', 0.5)],
        "shy": [('c5', 0.1), ('e5', 0.3), ('c5', 0.1), ('e5', 0.4)],
        "sleepy": [('g4', 0.5), ('f4', 0.5), ('e4', 0.7)],
        "speaking": [('c5', 0.1), ('d5', 0.1), ('e5', 0.1)] * 3,
        "surprising": [('g6', 0.3)],
    }

    def __init__(self):
        """
        Initializes the RobotSoundPlayer.
        """
        try:
            self.pi = pigpio.pi()
            if not self.pi.connected:
                raise IOError("Could not connect to pigpio daemon.")
        except Exception as e:
            print(f"Error initializing pigpio: {e}")
            self.pi = None
            return

        try:
            # Assumes buzzer.json is in the root of the NinjaRobotV3 project
            config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../', 'buzzer.json'))
            with open(config_path, 'r') as f:
                config = json.load(f)
                pin = config['pin']
            self.buzzer = Buzzer(self.pi, pin)
        except FileNotFoundError:
            print("Error: buzzer.json not found. Please run 'pi0buzzer init <pin>' first.")
            self.buzzer = None
        except Exception as e:
            print(f"Error initializing buzzer: {e}")
            self.buzzer = None

    def play(self, emotion: str):
        """
        Plays the sound for the given emotion.
        """
        if not self.buzzer:
            print("Buzzer is not initialized.")
            return

        if emotion not in self.SOUNDS:
            print(f"Unknown emotion: {emotion}")
            return

        melody = self.SOUNDS[emotion]
        print(f"Playing sound for: {emotion}")

        for note_name, duration in melody:
            if note_name == 'pause':
                time.sleep(duration)
                continue

            frequency = self.NOTES.get(note_name)
            if frequency:
                self.buzzer.play_sound(frequency, duration)
                time.sleep(0.01)  # Brief pause between notes
            else:
                print(f"Warning: Note '{note_name}' not found.")
        
    def cleanup(self):
        """
        Cleans up resources.
        """
        if self.buzzer:
            self.buzzer.off()
        if self.pi and self.pi.connected:
            self.pi.stop()
        print("\nRobot Sound Player shutting down.")

def main():
    """
    Main function to run the interactive sound player.
    """
    player = RobotSoundPlayer()
    if not player.pi or not player.buzzer:
        return # Initialization failed

    emotions = sorted(list(player.SOUNDS.keys()))

    try:
        while True:
            print("\n--- Robot Emotion Sound Menu ---")
            for i, emotion in enumerate(emotions, 1):
                print(f"{i}. {emotion.capitalize()}")
            print("---------------------------------")
            choice = input("Enter a number to play a sound, or 'q' to quit: ")

            if choice.lower() == 'q':
                break
            
            try:
                index = int(choice) - 1
                if 0 <= index < len(emotions):
                    player.play(emotions[index])
                else:
                    print("Invalid number. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number or 'q'.")

    except KeyboardInterrupt:
        print("\nCaught interrupt, shutting down.")
    finally:
        player.cleanup()

if __name__ == "__main__":
    main()
