import pigpio
import time
import json
import os
import sys
import tty
import termios
import select

class Buzzer:
    def __init__(self, pi, pin, config_file='buzzer.json'):
        self.pi = pi
        self.pin = pin
        self.config_file = config_file
        self.pi.set_mode(self.pin, pigpio.OUTPUT)
        self.save_config()
        # self.play_hello() # remove auto play hello

    def save_config(self):
        config = {'pin': self.pin}
        with open(self.config_file, 'w') as f:
            json.dump(config, f)

    def play_hello(self):
        # A simple melody
        notes = [
            (262, 0.2),  # C4
            (294, 0.2),  # D4
            (330, 0.2),  # E4
            (349, 0.2),  # F4
            (392, 0.2),  # G4
            (440, 0.2),  # A4
            (494, 0.2),  # B4
            (523, 0.4),  # C5
        ]
        for note, duration in notes:
            self.pi.set_PWM_frequency(self.pin, note)
            self.pi.set_PWM_dutycycle(self.pin, 128)  # 50% duty cycle
            time.sleep(duration)
        self.pi.set_PWM_dutycycle(self.pin, 0)  # Stop PWM

    def play_sound(self, frequency, duration):
        self.pi.set_PWM_frequency(self.pin, frequency)
        self.pi.set_PWM_dutycycle(self.pin, 128)  # 50% duty cycle
        time.sleep(duration)
        self.pi.set_PWM_dutycycle(self.pin, 0)  # Stop PWM

    def off(self):
        self.pi.set_PWM_dutycycle(self.pin, 0)  # Stop PWM

class MusicBuzzer(Buzzer):
    def __init__(self, pi, pin, config_file='buzzer.json'):
        super().__init__(pi, pin, config_file)

        # User-provided frequencies for 3 octaves
        self.notes = {
            # Low Octave (C4-B4) - Bottom row
            'z': 262,  # Low 1 DO (C4)
            'x': 294,  # Low 2 RE (D4)
            'c': 330,  # Low 3 MI (E4)
            'v': 349,  # Low 4 FA (F4)
            'b': 392,  # Low 5 SO (G4)
            'n': 440,  # Low 6 LA (A4)
            'm': 494,  # Low 7 XI (B4)

            # Middle Octave (C5-B5) - Middle row
            'a': 523,  # Middle 1 DO (C5)
            's': 587,  # Middle 2 RE (D5)
            'd': 659,  # Middle 3 MI (E5)
            'f': 698,  # Middle 4 FA (F5)
            'g': 784,  # Middle 5 SO (G5)
            'h': 880,  # Middle 6 LA (A5)
            'j': 988,  # Middle 7 XI (B5)

            # High Octave (C6-B6) - Top row
            'q': 1046, # High 1 DO (C6)
            'w': 1175, # High 2 RE (D6)
            'e': 1318, # High 3 MI (E6)
            'r': 1397, # High 4 FA (F6)
            't': 1568, # High 5 SO (G6)
            'y': 1760, # High 6 LA (A6)
            'u': 1967, # High 7 XI (B6)
        }

    def play_song(self, song):
        """Plays a song defined as a list of (note_key, duration) tuples."""
        for note_key, duration in song:
            frequency = 0
            if note_key in self.notes:
                frequency = self.notes[note_key]
            elif note_key == 'b_flat_4':
                # Special handling for B-flat 4, not in the C-major keyboard map
                frequency = 466
            
            if frequency > 0:
                self.pi.set_PWM_frequency(self.pin, frequency)
                self.pi.set_PWM_dutycycle(self.pin, 128)
                time.sleep(duration)
                self.pi.set_PWM_dutycycle(self.pin, 0) # Brief pause between notes
                time.sleep(0.05)
            else: # Handles 'pause'
                time.sleep(duration)

    def play_music(self):
        print("🎵 Playing 'Happy Birthday'...")

        # Melody for "Happy Birthday"
        # Format: (note_key, duration_in_seconds)
        happy_birthday_melody = [
            ('z', 0.25), ('z', 0.12), ('x', 0.37), ('z', 0.37), ('v', 0.37), ('c', 0.75), ('pause', 0.37),
            ('z', 0.25), ('z', 0.12), ('x', 0.37), ('z', 0.37), ('b', 0.37), ('v', 0.75), ('pause', 0.37),
            ('z', 0.25), ('z', 0.12), ('a', 0.37), ('n', 0.37), ('v', 0.37), ('c', 0.37), ('x', 0.75), ('pause', 0.37),
            ('b_flat_4', 0.25), ('b_flat_4', 0.12), ('n', 0.37), ('v', 0.37), ('b', 0.37), ('v', 0.75),
        ]
        self.play_song(happy_birthday_melody)
        
        print("\n🎵 Play 3 Octaves of C Major with your keyboard!")
        print("High Octave (C6): q, w, e, r, t, y, u")
        print("Mid Octave  (C5): a, s, d, f, g, h, j")
        print("Low Octave  (C4): z, x, c, v, b, n, m")
        print("Press 'esc' to quit.")
        input("Press Enter to start...")

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            last_char = None
            while True:
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    char = sys.stdin.read(1)
                    if ord(char) == 27:  # ESC key
                        break
                    if char in self.notes:
                        if char != last_char:
                            self.pi.set_PWM_frequency(self.pin, self.notes[char])
                            self.pi.set_PWM_dutycycle(self.pin, 128)
                            last_char = char
                else:
                    self.pi.set_PWM_dutycycle(self.pin, 0)
                    last_char = None

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            self.off()
