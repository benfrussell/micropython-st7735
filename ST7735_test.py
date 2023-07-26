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

gc.collect()
mem = gc.mem_free()

tft = ST7735()
tft.tft_initialize()

gc.collect()
print(f"ST7735 size: {mem - gc.mem_free()} bytes")

tft.fill_screen(0xffff)

text = "Big Test!"

start = time.ticks_ms()
tft.draw_fast_text(text, 5, 10, 0x0000)
print(f"Fast text time: {time.ticks_diff(time.ticks_ms(), start)} ms")

start = time.ticks_ms()
tft.draw_text(text, 5, 20, 0x0000)
print(f"Text time: {time.ticks_diff(time.ticks_ms(), start)} ms")

y = 0
while y < 200:
    tft.draw_fast_text(text, 5, 30, random_16bit_color())
    y += 1