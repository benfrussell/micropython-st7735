import gc
import time
import random
from ST7735 import ST7735

def random_16bit_color():
    # Generate random values for red, green, and blue components
    red = random.randint(0, 31)    # 5 bits (0 to 31)
    green = random.randint(0, 63)  # 6 bits (0 to 63)
    blue = random.randint(0, 31)   # 5 bits (0 to 31)

    # Combine the color components into a 16-bit color representation
    color_16bit = (red << 11) | (green << 5) | blue

    return color_16bit

tft = ST7735(cache_font=True)
tft.tft_initialize()

start = time.ticks_ms()
fills = 20
while fills > 0:
    tft.fill_screen(random_16bit_color())
    fills -= 1
print(f"Fill time: {time.ticks_diff(time.ticks_ms(), start) / 20} ms")

start = time.ticks_ms()
for r in range(11):
    text = "".join([chr(ci) for ci in range(33 + (r * 9), 42 + (r * 9))])
    tft.draw_text(text, 5, r * 8 + 5, 0x0000)
print(f"Slow text time: {time.ticks_diff(time.ticks_ms(), start)} ms")

tft.fill_screen(0xffff)

start = time.ticks_ms()
for r in range(11):
    text = "".join([chr(ci) for ci in range(33 + (r * 9), 42 + (r * 9))])
    tft.draw_fast_text(text, 5, r * 8 + 5, 0x0000)
print(f"Cached text time: {time.ticks_diff(time.ticks_ms(), start)} ms")

tft.fill_screen(0xffff)

start = time.ticks_ms()
lines = 20
while lines > 0:
    tft.draw_line(0, random.randint(0, 160), 80, random.randint(0, 160), random_16bit_color())
    lines -= 1
print(f"Line time: {time.ticks_diff(time.ticks_ms(), start) / 20} ms")

tft.fill_screen(0xffff)

start = time.ticks_ms()
tft.draw_ellipse(40, 40, 37, 37, 0xF000, fill=False)
print(f"Ellipse outline time: {time.ticks_diff(time.ticks_ms(), start)} ms")

start = time.ticks_ms()
tft.draw_ellipse(40, 120, 37, 37, 0xF000)
print(f"Ellipse fill time: {time.ticks_diff(time.ticks_ms(), start)} ms")