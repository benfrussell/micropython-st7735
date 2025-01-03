import gc
import time
import random
from ST7735 import ST7735
from svg import SVG

def random_16bit_color() -> bytes:
    # Generate random values for red, green, and blue components
    red = random.randint(0, 31)    # 5 bits (0 to 31)
    green = random.randint(0, 63)  # 6 bits (0 to 63)
    blue = random.randint(0, 31)   # 5 bits (0 to 31)

    # Combine the color components into a 16-bit color representation
    color_16bit = (red << 11) | (green << 5) | blue

    return color_16bit.to_bytes(2, 'big')

def test_tft(tft):
    tft.tft_initialize()

    start = time.ticks_ms()
    fills = 20
    while fills > 0:
        tft.fill_screen(random_16bit_color())
        fills -= 1
    print(f"Fill time: {time.ticks_diff(time.ticks_ms(), start) / 20} ms")
    time.sleep_ms(1500)

    test_text(tft)
    time.sleep_ms(1500)
    test_lines(tft)
    time.sleep_ms(1500)
    test_ellipses(tft)
    time.sleep_ms(1500)
    test_poly(tft)
    time.sleep_ms(1500)

    tft.fill_screen(b'\xff\xff')

    start = time.ticks_ms()
    t = 1
    while t <= 40:
        tft.draw_rect(0, 0, 80, 160, b'\x00\x00', False, t)
        t += 1
    print(f"Rect outline time: {time.ticks_diff(time.ticks_ms(), start) / 40} ms")
    time.sleep_ms(1500)

def test_text(tft):
    tft.fill_screen(b'\xff\xff')

    start = time.ticks_ms()
    for r in range(11):
        text = "".join([chr(ci) for ci in range(33 + (r * 9), 42 + (r * 9))])
        tft.draw_text(text, 5, r * 8 + 5, b'\x00\x00')
    print(f"Text time: {time.ticks_diff(time.ticks_ms(), start)} ms")

def test_ellipses(tft):
    tft.fill_screen(b'\xff\xff')
    start = time.ticks_ms()
    tft.draw_ellipse(40, 40, 37, 37, b'\xF0\x00', fill=False)
    print(f"Ellipse outline time: {time.ticks_diff(time.ticks_ms(), start)} ms")

    start = time.ticks_ms()
    tft.draw_ellipse(40, 120, 37, 37, b'\xF0\x00')
    print(f"Ellipse fill time: {time.ticks_diff(time.ticks_ms(), start)} ms")

def test_lines(tft):
    tft.fill_screen(b'\xff\xff')
    start = time.ticks_ms()
    lines = 20
    while lines > 0:
        tft.draw_line(0, random.randint(0, 160), 80, random.randint(0, 160), random_16bit_color())
        lines -= 1
    print(f"Line time: {time.ticks_diff(time.ticks_ms(), start) / 20} ms")

def test_poly(tft):
    tft.fill_screen(b'\xff\xff')
    start = time.ticks_ms()
    tft.draw_poly(0, 0, [18, 70, 33, 70, 40, 55, 47, 70, 62, 70, 51, 78, 58, 94, 40, 82, 22, 94, 29, 78], b'\xAA\xAA', True, False)
    print(f"Poly time: {time.ticks_diff(time.ticks_ms(), start)} ms")

def test_rotation(tft):
    tft.tft_initialize()
    tft.set_rotation(0)
    test_text(tft)
    tft.set_rotation(2)
    test_text(tft)
    tft.set_rotation(1)
    test_text(tft)
    tft.set_rotation(3)
    test_text(tft)
    tft.set_rotation(0)

def test_mirror(tft):
    tft.tft_initialize()
    tft.set_rotation(0)
    test_text(tft)
    tft.set_rotation(0, mirror_x=True)
    test_text(tft)
    tft.set_rotation(0, mirror_y=True)
    test_text(tft)
    tft.set_rotation(0, mirror_x=True, mirror_y=True)
    test_text(tft)
    tft.set_rotation(0)
    test_text(tft)

def test_svg(tft):
    tft.tft_initialize()
    with open("test.svg") as f:
        svg_test = SVG.read_svg(f)
    tft.set_rotation(1)
    tft.fill_screen(b'\xff\xff')

    start = time.ticks_ms()
    tft.draw_svg(svg_test)
    print(f"Draw svg time: {time.ticks_diff(time.ticks_ms(), start)} ms")

    start = time.ticks_ms()
    c_svg = tft.create_cached_svg(svg_test)
    print(f"Cache svg time: {time.ticks_diff(time.ticks_ms(), start)} ms")

    time.sleep(0.5)
    tft.fill_screen(b'\xff\xff')

    start = time.ticks_ms()
    tft.draw_cached_svg(c_svg)
    print(f"Draw cached svg time: {time.ticks_diff(time.ticks_ms(), start)} ms")

gc.collect()
before = gc.mem_alloc()
#     def __init__(self, dc=22, cs=21, rt=20, sck=18, mosi=19, miso=16, spi_port=0, baud=62_500_000, height=160, width=80, cache_font=True):
tft = ST7735(dc=22, cs=21, rt=15, sck=18, mosi=19, miso=16, spi_port=0)
#test_svg(tft)
test_tft(tft)
gc.collect()
print(f"{gc.mem_alloc() - before} bytes in memory")



