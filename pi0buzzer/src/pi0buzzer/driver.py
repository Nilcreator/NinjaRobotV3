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

        # Correct frequencies for C Major Scale (C, D, E, F, G, A, B, C)
        self.notes = {
            # Middle C (C4 - B4)
            'a': 262,  # C4
            's': 294,  # D4
            'd': 330,  # E4
            'f': 349,  # F4
            'g': 392,  # G4
            'h': 440,  # A4
            'j': 494,  # B4

            # High C (C5 - B5)
            'q': 523,  # C5
            'w': 587,  # D5
            'e': 659,  # E5
            'r': 698,  # F5
            't': 784,  # G5
            'y': 880,  # A5
            'u': 988,  # B5

            # Low C (C3 - B3)
            'z': 131,  # C3
            'x': 147,  # D3
            'c': 165,  # E3
            'v': 175,  # F3
            'b': 196,  # G3
            'n': 220,  # A3
            'm': 247,  # B3
        }

    def play_music(self):
        print("🎵 Play the C Major Scale with your keyboard!")
        print("Middle C: a, s, d, f, g, h, j")
        print("High C:   q, w, e, r, t, y, u")
        print("Low C:    z, x, c, v, b, n, m")
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
