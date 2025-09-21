
import pigpio
import time
import sys
import select
import tty
import termios
import os

# Add the parent directory to the path to find the vl53l0x_pigpio library
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from vl53l0x_pigpio import VL53L0X

class DistanceDetector:
    """
    A class to detect distance using the VL53L0X sensor.
    """
    def __init__(self):
        try:
            self.pi = pigpio.pi()
            if not self.pi.connected:
                raise IOError("Could not connect to pigpio daemon.")
        except Exception as e:
            print(f"Error initializing pigpio: {e}", file=sys.stderr)
            self.pi = None

    def timed_detection(self, count: int, delay: float):
        """
        Performs a specified number of distance measurements with a delay.
        """
        if not self.pi:
            return

        print(f"Starting timed detection: {count} measurements, {delay}s delay...")
        try:
            with VL53L0X(self.pi) as tof:
                for i in range(count):
                    distance = tof.get_range()
                    if distance > 0:
                        print(f"Measurement {i + 1}/{count}: {distance} mm")
                    else:
                        print(f"Measurement {i + 1}/{count}: Out of range")
                    time.sleep(delay)
        except Exception as e:
            print(f"An error occurred during timed detection: {e}", file=sys.stderr)

    def continuous_detection(self):
        """
        Performs continuous distance measurement at 5Hz until 'q' is pressed.
        """
        if not self.pi:
            return

        print("Starting continuous detection at 5Hz. Press 'q' to quit.")
        
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        
        try:
            tty.setraw(sys.stdin.fileno())
            with VL53L0X(self.pi) as tof:
                while True:
                    # Check for user input
                    if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                        if sys.stdin.read(1) == 'q':
                            break

                    distance = tof.get_range()
                    if distance > 0:
                        # Use carriage return to print on the same line
                        print(f"Distance: {distance:4d} mm", end="\r")
                    else:
                        print("Distance: Out of range", end="\r")
                    
                    time.sleep(0.2) # 5Hz

        except Exception as e:
            print(f"An error occurred during continuous detection: {e}", file=sys.stderr)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            print("\nStopping continuous detection.")

    def cleanup(self):
        if self.pi and self.pi.connected:
            self.pi.stop()

def main():
    """Main function to run the interactive distance detector."""
    detector = DistanceDetector()
    if not detector.pi:
        return

    try:
        while True:
            print("\n--- Distance Detector Menu ---")
            print("1. Timed Detection")
            print("2. Continuous Detection")
            print("----------------------------")
            choice = input("Choose an option (or 'q' to quit): ")

            if choice == '1':
                try:
                    count = int(input("Enter number of measurements (e.g., 5): "))
                    delay = float(input("Enter delay between measurements in seconds (e.g., 1.0): "))
                    detector.timed_detection(count, delay)
                except ValueError:
                    print("Invalid input. Please enter numbers for count and delay.")
            elif choice == '2':
                detector.continuous_detection()
            elif choice.lower() == 'q':
                break
            else:
                print("Invalid choice. Please try again.")

    except KeyboardInterrupt:
        print("\nCaught interrupt, shutting down.")
    finally:
        detector.cleanup()

if __name__ == '__main__':
    main()
