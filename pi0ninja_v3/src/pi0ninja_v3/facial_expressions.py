import time
import math
import threading
from PIL import Image, ImageDraw, ImageFont

from pi0disp.disp.st7789v import ST7789V

class AnimatedFaces:
    """
    Generates and displays programmatically drawn, animated facial expressions
    based on a unified design style. This class is thread-safe.
    """

    def __init__(self, lcd: ST7789V):
        self.lcd = lcd
        self.width, self.height = lcd.width, lcd.height
        self.bg_color = "black"
        self.face_color = "white"
        self.blush_color = "#FF69B4"
        self.tear_color = "#00BFFF"

        # Threading control
        self._animation_thread = None
        self._stop_event = threading.Event()

        # Style guide
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        self.eye_y = self.center_y - 35
        self.mouth_y = self.center_y + 50
        self.eye_offset = 60
        self.eye_radius = 45
        self.pupil_radius = 20
        self.line_width = 12

        try:
            self.font = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", 50)
        except IOError:
            self.font = ImageFont.load_default()

    def _get_blank_image(self):
        return Image.new("RGB", (self.width, self.height), self.bg_color)

    def _animation_loop(self, duration_s, frame_logic):
        """The actual loop that runs in a thread to draw frames."""
        start_time = time.time()
        while not self._stop_event.is_set() and (time.time() - start_time < duration_s):
            image = self._get_blank_image()
            draw = ImageDraw.Draw(image)
            frame_logic(draw, time.time() - start_time)
            self.lcd.display(image)
            time.sleep(1/60) # ~60 FPS

    def _start_animation(self, duration_s, frame_logic):
        """Stops any running animation and starts a new one."""
        self.stop() # Safely stop the previous thread

        self._stop_event.clear()
        self._animation_thread = threading.Thread(
            target=self._animation_loop, 
            args=(duration_s, frame_logic)
        )
        self._animation_thread.start()

    def stop(self):
        """Stops the current animation thread and waits for it to exit."""
        if self._animation_thread and self._animation_thread.is_alive():
            self._stop_event.set()
            self._animation_thread.join()

    # --- Base Drawing Helpers ---

    def _draw_base_eyes(self, draw, left_pupil_shift=(0, 0), right_pupil_shift=(0, 0)):
        lx, ly = self.center_x - self.eye_offset, self.eye_y
        draw.ellipse([lx - self.eye_radius, ly - self.eye_radius, lx + self.eye_radius, ly + self.eye_radius], fill=self.face_color)
        lpx, lpy = lx + left_pupil_shift[0], ly + left_pupil_shift[1]
        draw.ellipse([lpx - self.pupil_radius, lpy - self.pupil_radius, lpx + self.pupil_radius, lpy + self.pupil_radius], fill=self.bg_color)

        rx, ry = self.center_x + self.eye_offset, self.eye_y
        draw.ellipse([rx - self.eye_radius, ry - self.eye_radius, rx + self.eye_radius, ry + self.eye_radius], fill=self.face_color)
        rpx, rpy = rx + right_pupil_shift[0], ry + right_pupil_shift[1]
        draw.ellipse([rpx - self.pupil_radius, rpy - self.pupil_radius, rpx + self.pupil_radius, rpy + self.pupil_radius], fill=self.bg_color)

    def _draw_happy_base(self, draw):
        self._draw_base_eyes(draw)
        eyebrow_y = self.eye_y - self.eye_radius - (self.line_width / 2) - 5
        draw.arc([self.center_x - self.eye_offset - 40, eyebrow_y - 40, self.center_x - self.eye_offset + 40, eyebrow_y], 0, 180, fill=self.face_color, width=self.line_width)
        draw.arc([self.center_x + self.eye_offset - 40, eyebrow_y - 40, self.center_x + self.eye_offset + 40, eyebrow_y], 0, 180, fill=self.face_color, width=self.line_width)
        draw.arc([self.center_x - 70, self.mouth_y - 50, self.center_x + 70, self.mouth_y + 50], 0, 180, fill=self.face_color)

    def _draw_sad_base(self, draw):
        pupil_shift = (0, 15)
        self._draw_base_eyes(draw, pupil_shift, pupil_shift)
        draw.line([self.center_x - self.eye_offset - 30, self.eye_y - 50, self.center_x - self.eye_offset + 10, self.eye_y - 70], fill=self.face_color, width=self.line_width)
        draw.line([self.center_x + self.eye_offset + 30, self.eye_y - 50, self.center_x + self.eye_offset - 10, self.eye_y - 70], fill=self.face_color, width=self.line_width)
        draw.arc([self.center_x - 60, self.mouth_y + 20, self.center_x + 60, self.mouth_y + 80], 180, 360, fill=self.face_color)

    # --- Animation Methods ---

    def play_idle(self, duration_s=float('inf')):
        print("Playing: Idle")
        def logic(draw, t):
            blink_cycle = (t * 2) % 3
            if blink_cycle < 0.15:
                draw.line([self.center_x - self.eye_offset - 30, self.eye_y, self.center_x - self.eye_offset + 30, self.eye_y], fill=self.face_color, width=self.line_width)
                draw.line([self.center_x + self.eye_offset - 30, self.eye_y, self.center_x + self.eye_offset + 30, self.eye_y], fill=self.face_color, width=self.line_width)
            else:
                self._draw_base_eyes(draw)
            draw.arc([self.center_x - 50, self.mouth_y - 10, self.center_x + 50, self.mouth_y + 10], 0, 180, fill=self.face_color)
        self._start_animation(duration_s, logic)

    def play_happy(self, duration_s=3):
        print("Playing: Happy")
        def logic(draw, t):
            self._draw_happy_base(draw)
        self._start_animation(duration_s, logic)

    def play_laughing(self, duration_s=3):
        print("Playing: Laughing")
        def logic(draw, t):
            self._draw_happy_base(draw)
            mouth_height = abs(math.sin(t * 15)) * 60
            draw.rectangle([self.center_x - 70, self.mouth_y, self.center_x + 70, self.mouth_y + mouth_height], fill=self.bg_color)
        self._start_animation(duration_s, logic)

    # ... (all other play_* methods are the same, they just call self._start_animation)
    def play_sad(self, duration_s=3):
        print("Playing: Sad")
        def logic(draw, t):
            self._draw_sad_base(draw)
        self._start_animation(duration_s, logic)

    def play_cry(self, duration_s=3):
        print("Playing: Cry")
        def logic(draw, t):
            self._draw_sad_base(draw)
            tear_y_base = self.eye_y + self.eye_radius
            tear_length = self.height - tear_y_base
            for i in range(3):
                tear_y = tear_y_base + (t * 200 + i * 40) % tear_length
                draw.line([self.center_x - self.eye_offset, tear_y, self.center_x - self.eye_offset, tear_y + 30], fill=self.tear_color, width=self.line_width)
        self._start_animation(duration_s, logic)

    def play_angry(self, duration_s=3):
        print("Playing: Angry")
        def logic(draw, t):
            shake = math.sin(t * 20) * 3
            self._draw_base_eyes(draw)
            draw.line([self.center_x - self.eye_offset - 40, self.eye_y - 30 + shake, self.center_x - self.eye_offset + 40, self.eye_y - 70 + shake], fill=self.face_color, width=self.line_width)
            draw.line([self.center_x + self.eye_offset + 40, self.eye_y - 30 + shake, self.center_x + self.eye_offset - 40, self.eye_y - 70 + shake], fill=self.face_color, width=self.line_width)
            draw.arc([self.center_x - 70, self.mouth_y - 20, self.center_x + 70, self.mouth_y + 80], 180, 360, fill=self.face_color)
        self._start_animation(duration_s, logic)

    def play_surprising(self, duration_s=3):
        print("Playing: Surprising")
        def logic(draw, t):
            open_factor = min(1, t * 4)
            pupil_radius_factor = 1 - (open_factor * 0.5)
            current_pupil_radius = self.pupil_radius * pupil_radius_factor
            lx, ly = self.center_x - self.eye_offset, self.eye_y
            draw.ellipse([lx - self.eye_radius, ly - self.eye_radius, lx + self.eye_radius, ly + self.eye_radius], fill=self.face_color)
            draw.ellipse([lx - current_pupil_radius, ly - current_pupil_radius, lx + current_pupil_radius, ly + current_pupil_radius], fill=self.bg_color)
            rx, ry = self.center_x + self.eye_offset, self.eye_y
            draw.ellipse([rx - self.eye_radius, ry - self.eye_radius, rx + self.eye_radius, ry + self.eye_radius], fill=self.face_color)
            draw.ellipse([rx - current_pupil_radius, ry - current_pupil_radius, rx + current_pupil_radius, ry + current_pupil_radius], fill=self.bg_color)
            mouth_radius = min(50, t * 120)
            draw.ellipse([self.center_x - mouth_radius, self.mouth_y - mouth_radius, self.center_x + mouth_radius, self.mouth_y + mouth_radius], fill=self.face_color)
        self._start_animation(duration_s, logic)

    def play_sleepy(self, duration_s=3):
        print("Playing: Sleepy")
        def logic(draw, t):
            open_factor = (math.cos(t * 1.5) + 1) / 2 * 0.9 + 0.05
            ly, ry = self.eye_y, self.eye_y
            draw.arc([self.center_x - self.eye_offset - self.eye_radius, ly - self.eye_radius, self.center_x - self.eye_offset + self.eye_radius, ly + self.eye_radius], 180, 360, fill=self.face_color)
            draw.arc([self.center_x + self.eye_offset - self.eye_radius, ry - self.eye_radius, self.center_x + self.eye_offset + self.eye_radius, ry + self.eye_radius], 180, 360, fill=self.face_color)
            draw.arc([self.center_x - self.eye_offset - self.eye_radius, ly - self.eye_radius, self.center_x - self.eye_offset + self.eye_radius, ly + self.eye_radius], 0, 180, fill=self.face_color, width=self.line_width)
            draw.arc([self.center_x + self.eye_offset - self.eye_radius, ry - self.eye_radius, self.center_x + self.eye_offset + self.eye_radius, ry + self.eye_radius], 0, 180, fill=self.face_color, width=self.line_width)
            draw.rectangle([0, self.eye_y - self.eye_radius, self.width, self.eye_y - self.eye_radius + (self.eye_radius*2)*(1-open_factor)], fill=self.bg_color)
            draw.arc([self.center_x - 20, self.mouth_y - 10, self.center_x + 20, self.mouth_y + 10], 0, 360, fill=self.face_color)
        self._start_animation(duration_s, logic)

    def play_speaking(self, duration_s=3):
        print("Playing: Speaking")
        def logic(draw, t):
            self._draw_base_eyes(draw)
            mouth_height = (math.sin(t * 15) + 1) / 2 * 40 + 10
            draw.ellipse([self.center_x - 50, self.mouth_y, self.center_x + 50, self.mouth_y + mouth_height], fill=self.face_color)
        self._start_animation(duration_s, logic)

    def play_shy(self, duration_s=3):
        print("Playing: Shy")
        def logic(draw, t):
            pupil_shift = (-20, 15)
            self._draw_base_eyes(draw, pupil_shift, pupil_shift)
            blush_y = self.eye_y + self.eye_radius / 2
            blush_radius = 25
            draw.ellipse([self.center_x - self.eye_offset - 15, blush_y, self.center_x - self.eye_offset + 35, blush_y + blush_radius], fill=self.blush_color)
            draw.ellipse([self.center_x + self.eye_offset - 35, blush_y, self.center_x + self.eye_offset + 15, blush_y + blush_radius], fill=self.blush_color)
            points = [self.center_x - 40, self.mouth_y+10, self.center_x - 20, self.mouth_y, self.center_x, self.mouth_y+10, self.center_x + 20, self.mouth_y, self.center_x + 40, self.mouth_y+10]
            draw.line(points, fill=self.face_color, width=self.line_width-2, joint="curve")
        self._start_animation(duration_s, logic)

    def play_embarrassing(self, duration_s=3):
        self.play_shy(duration_s)

    def play_scary(self, duration_s=3):
        print("Playing: Scary")
        def logic(draw, t):
            current_pupil_radius = 10
            shake = math.sin(t * 50) * 4
            lx, ly = self.center_x - self.eye_offset, self.eye_y
            draw.ellipse([lx - self.eye_radius, ly - self.eye_radius, lx + self.eye_radius, ly + self.eye_radius], fill=self.face_color)
            lpx, lpy = lx, ly + shake
            draw.ellipse([lpx - current_pupil_radius, lpy - current_pupil_radius, lpx + current_pupil_radius, lpy + current_pupil_radius], fill=self.bg_color)
            rx, ry = self.center_x + self.eye_offset, self.eye_y
            draw.ellipse([rx - self.eye_radius, ry - self.eye_radius, rx + self.eye_radius, ry + self.eye_radius], fill=self.face_color)
            rpx, rpy = rx, ry + shake
            draw.ellipse([rpx - current_pupil_radius, rpy - current_pupil_radius, rpx + current_pupil_radius, rpy + current_pupil_radius], fill=self.bg_color)
            draw.arc([self.center_x - 70, self.mouth_y - 20, self.center_x + 70, self.mouth_y + 80], 180, 360, fill=self.face_color)
        self._start_animation(duration_s, logic)

    def play_exciting(self, duration_s=3):
        print("Playing: Exciting")
        def logic(draw, t):
            star_points = 10
            for eye_center_x in [self.center_x - self.eye_offset, self.center_x + self.eye_offset]:
                angle = math.pi * 2 / star_points
                points = []
                for i in range(star_points):
                    r = self.eye_radius if i % 2 == 0 else self.eye_radius / 2
                    points.append((eye_center_x + r * math.cos(angle * i + t*10), self.eye_y + r * math.sin(angle * i + t*10)))
                draw.polygon(points, fill=self.face_color)
            draw.arc([self.center_x - 70, self.mouth_y - 50, self.center_x + 70, self.mouth_y + 50], 0, 180, fill=self.face_color)
        self._start_animation(duration_s, logic)

    def play_confusing(self, duration_s=3):
        print("Playing: Confusing")
        def logic(draw, t):
            self._draw_base_eyes(draw, (-15, 0), (15, 0))
            draw.arc([self.center_x - self.eye_offset - 40, self.eye_y - 90, self.center_x - self.eye_offset + 40, self.eye_y - 10], 0, 180, fill=self.face_color, width=self.line_width)
            points = [self.center_x - 50, self.mouth_y+10, self.center_x - 25, self.mouth_y-10, self.center_x, self.mouth_y+10, self.center_x + 25, self.mouth_y-10, self.center_x + 50, self.mouth_y+10]
            draw.line(points, fill=self.face_color, width=self.line_width-2, joint="curve")
            if t > 0.5:
                draw.text((self.center_x + self.eye_offset + 10, self.eye_y - 100), "?", font=self.font, fill=self.face_color)
        self._start_animation(duration_s, logic)
