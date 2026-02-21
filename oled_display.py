import time
import board
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306


class OLEDDisplay:
    def __init__(self):
        self.WIDTH = 128
        self.HEIGHT = 64

        i2c = busio.I2C(board.SCL, board.SDA)
        self.oled = adafruit_ssd1306.SSD1306_I2C(
            self.WIDTH, self.HEIGHT, i2c, addr=0x3C
        )

        self.image = Image.new("1", (self.WIDTH, self.HEIGHT))
        self.draw = ImageDraw.Draw(self.image)

        # ==========================
        # FONT CONFIG
        # ==========================
        self.font_title = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12
        )

        self.font_small = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14
        )

        self.font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

        # Urut dari terbesar → terkecil
        self.font_sizes = [36, 34, 32, 30, 28, 26, 24, 22, 20]

        # Preload font (biar ringan)
        self.font_cache = {
            size: ImageFont.truetype(self.font_path, size)
            for size in self.font_sizes
        }

        # Blink state
        self.blink_state = True
        self.last_blink = 0

        self.clear()

    # ==========================
    # BASIC CONTROL
    # ==========================
    def clear(self):
        self.oled.fill(0)
        self.oled.show()

    # ==========================
    # BOOT SEQUENCE (non blocking lama)
    # ==========================
    def boot_sequence(self):
        self._screen("HOUR METER", "Booting...")
        time.sleep(0.8)

        self._screen("Initializing", "")
        time.sleep(0.8)

        self._screen("SYSTEM READY", "")
        time.sleep(0.8)

    # ==========================
    # MAIN UPDATE
    # ==========================
    def update(self, hm_display, hms_display, state_on):

        # Blink hanya saat ON
        if state_on:
            if time.time() - self.last_blink > 0.5:
                self.blink_state = not self.blink_state
                self.last_blink = time.time()
        else:
            self.blink_state = True

        self.draw.rectangle((0, 0, self.WIDTH, self.HEIGHT), fill=0)

        # Title
        self._center("HOUR METER", 0, self.font_title)

        # HM BESAR (auto-scale)
        if self.blink_state:
            dynamic_font = self._get_dynamic_font(hm_display)
            self._center(hm_display, 16, dynamic_font)

        # Time kecil
        self._center(hms_display, 50, self.font_small)

        self._show()

    # ==========================
    # DYNAMIC FONT SCALE
    # ==========================
    def _get_dynamic_font(self, text):
        for size in self.font_sizes:  # mulai dari terbesar
            font = self.font_cache[size]
            bbox = self.draw.textbbox((0, 0), text, font=font)
            width = bbox[2] - bbox[0]

            if width <= self.WIDTH - 4:  # margin aman
                return font

        return self.font_cache[self.font_sizes[-1]]

    # ==========================
    # HELPER
    # ==========================
    def _center(self, text, y, font):
        bbox = self.draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        x = (self.WIDTH - w) // 2
        self.draw.text((x, y), text, font=font, fill=255)

    def _screen(self, line1, line2):
        self.draw.rectangle((0, 0, self.WIDTH, self.HEIGHT), fill=0)
        self._center(line1, 20, self.font_title)
        self._center(line2, 40, self.font_small)
        self._show()

    def _show(self):
        self.oled.image(self.image)
        self.oled.show()
