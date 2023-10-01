from machine import Pin, SPI
import time
import framebuf
from array import array
from math import ceil, log, floor

ST7735_NOP          = const(0x00)
ST7735_SWRESET      = const(0x01)
ST7735_RDDID        = const(0x04)
ST7735_RDDST        = const(0x09)
ST7735_SLPIN        = const(0x10)
ST7735_SLPOUT       = const(0x11)
ST7735_PTLON        = const(0x12)
ST7735_NORON        = const(0x13)
ST7735_INVOFF       = const(0x20)
ST7735_INVON        = const(0x21)
ST7735_DISPOFF      = const(0x28)
ST7735_DISPON       = const(0x29)
ST7735_CASET        = const(0x2A)
ST7735_RASET        = const(0x2B)
ST7735_RAMWR        = const(0x2C)
ST7735_RAMRD        = const(0x2E)
ST7735_PTLAR        = const(0x30)
ST7735_VSCRDEF      = const(0x33)
ST7735_COLMOD       = const(0x3A)
ST7735_MADCTL       = const(0x36)
ST7735_VSCRSADD     = const(0x37)
ST7735_FRMCTR1      = const(0xB1)
ST7735_FRMCTR2      = const(0xB2)
ST7735_FRMCTR3      = const(0xB3)
ST7735_INVCTR       = const(0xB4)
ST7735_DISSET5      = const(0xB6)
ST7735_PWCTR1       = const(0xC0)
ST7735_PWCTR2       = const(0xC1)
ST7735_PWCTR3       = const(0xC2)
ST7735_PWCTR4       = const(0xC3)
ST7735_PWCTR5       = const(0xC4)
ST7735_VMCTR1       = const(0xC5)
ST7735_RDID1        = const(0xDA)
ST7735_RDID2        = const(0xDB)
ST7735_RDID3        = const(0xDC)
ST7735_RDID4        = const(0xDD)
ST7735_PWCTR6       = const(0xFC)
ST7735_GMCTRP1      = const(0xE0)
ST7735_GMCTRN1      = const(0xE1)

init_cmds = [
    # SLPOUT - Sleep out & booster on
    [ST7735_SLPOUT],
    # Frame rate commands
    # Frame rate = 333kHz / ( (param1 + 20) * (160 Lines + param2 + param3) )      
    # Params: RTNA set 1-line period (0x02), FPA: front porch (0x2D), BPA: back porch (0x2E)
    # Range: RTNA 0-7; FPA 0-63; BPA 1-63
    # FRMCTR1 - Frame rate control (In normal mode/Full colors)  
    [ST7735_FRMCTR1, 0x01, 0x2D],     
    # FRMCTR2 - Frame rate control (In Idle mode/8-colors)                          
    [ST7735_FRMCTR2, 0x01, 0x2D],
    # FRMCTR3 - Frame rate control (In Partial mode/full colors) 
    # Params 1-3 Line inversion mode; Params 4-6 Frame inversion mode
    [ST7735_FRMCTR3, 0x01, 0x2C, 0x2D, 0x01, 0x2C, 0x2D],
    # INVCTR - Display Inversion Control
    # Params: 0 - Line Inversion, 1 - Frame Inversion
    # 0b0000000X - Full Colors Normal Mode
    # 0b000000X0 - Idle Mode
    # 0b00000X00 - Full Colors Partial Mode
    [ST7735_INVCTR, 0x07],
    # DISSET5 - Signal & display configuration
    [ST7735_DISSET5, 0xA2, 0x02, 0x84],
    # PWCTR1 - GVDD voltage & AVDD uA
    [ST7735_PWCTR1, 0xA2, 0x02, 0x84],
    # PWCTR2 - Supply power level for VGH & VGL
    [ST7735_PWCTR2, 0xC5],
    # PWCTR3 - Set amplifier current & booster cycles (Full Colors Normal Mode)
    [ST7735_PWCTR3, 0x0A, 0x00],
    # PWCTR4 - Set amplifier current & booster cycles (Idle Mode)
    [ST7735_PWCTR4, 0x8A, 0x2A],
    # PWCTR5 - Set amplifier current & booster cycles (Full Colors Partial Mode)
    [ST7735_PWCTR5, 0x8A, 0xEE],
    # VMCTR1 - Set VCOMH & VCOML voltage
    [ST7735_VMCTR1, 0x0E],
    # INVOFF - Leave display inversion mode
    [ST7735_INVOFF],
    # COLMOD - Interface Pixel Format
    # 0x03 - 12-bit/pixel; 0x05 - 16-bit/pixel; 0x05 - 18-bit/pixel;
    [ST7735_COLMOD, 0x05],
    # CASET - Set column range
    [ST7735_CASET, 0x00,0x00,0x00,0x4F],
    # RASET - Set row range
    [ST7735_RASET, 0x00,0x00,0x00,0x9F],
    # Gamma commands
    # Param 1 - High level adjustment; Param 2-15 - Mid level adjustment; Param 16 - Low level adjustment
    # GMCTRP1 - Gamma ('+' polarity)
    [ST7735_GMCTRP1, 0x02, 0x1C, 0X07, 0X12, 0X37, 0X32, 0x29, 0x2D, 0X29, 0X25, 0X2B, 0X39, 0X00, 0X01, 0X03, 0x10],
    # GMCTRN1 - Gamma ('-' polarity)
    [ST7735_GMCTRN1, 0x03, 0x1D, 0X07, 0X06, 0X2E, 0X2C, 0x29, 0x2D, 0X2E, 0X2E, 0X37, 0X3F, 0X00, 0X00, 0X02, 0x10],
    # NORON - Normal display mode on
    [ST7735_NORON],
    # DISPON - Display on
    [ST7735_DISPON]
]

def int16_to_bytes(i: int):
    return bytes([(i >> 8) & 0xFF, i & 0xFF])

def rgb_to_565(rgb):
    r, g, b = rgb
    # Convert RGB values to 5-6-5 format
    r5 = (r >> 3) & 0x1F  # 5 bits for red
    g6 = (g >> 2) & 0x3F  # 6 bits for green
    b5 = (b >> 3) & 0x1F  # 5 bits for blue
    return (r5 << 11) | (g6 << 5) | b5

bitmask = const((128, 64, 32, 16, 8, 4, 2, 1))
bitmask_inv = const((127, 191, 223, 239, 247, 251, 253, 254))

def yield_px_in_row(framebuf, buf_width, y, start_x=0, end_x=80):
    bottom_pos = y * buf_width + start_x
    top_pos = bottom_pos + end_x
    start_byte = floor(bottom_pos / 8)
    pos = start_byte * 8
    for b in framebuf[start_byte:ceil(top_pos / 8) + 1]:
        while b > 0:
            bitlen = 7 - int(log(b,2))
            b = b & bitmask_inv[bitlen]
            new_pos = pos + bitlen
            if new_pos < bottom_pos:
                continue
            elif new_pos > top_pos:
                return
            # Yield the x
            yield new_pos % buf_width
        pos += 8

def yield_lines_in_row(framebuf, buf_width, y, start_x=0, end_x=80):
    next_x = start_x
    line_width = 0
    for px in yield_px_in_row(framebuf, buf_width, y, start_x, end_x):
        if px == next_x:
            line_width += 1
            next_x += 1
            continue
        elif line_width > 0:
            yield next_x - line_width, next_x - 1
        next_x = px + 1
        line_width = 1
    if line_width > 0:
        yield next_x - line_width, next_x - 1

def set_mono_framebuf_pixel(framebuf, buf_width, x, y, p):
    pos = (y * buf_width) + x
    mod = pos % 8
    pos = int((pos - mod) / 8)
    if p == 0:
        framebuf[pos] = framebuf[pos] & bitmask_inv[mod]
    else:
        framebuf[pos] = framebuf[pos] | bitmask[mod]

class ST7735:
    def __init__(self, dc=22, cs=21, rt=20, sck=18, mosi=19, miso=16, spi_port=0, baud=62_500_000, height=160, width=80, cache_font=True):
        self.dc_pin = Pin(dc, Pin.OUT, value=1)
        self.cs_pin = Pin(cs, Pin.OUT, value=1)
        self.rt_pin = Pin(rt, Pin.OUT, value=1)

        self.sck_pin = Pin(sck, Pin.ALT_SPI)
        self.mosi_pin = Pin(mosi, Pin.ALT_SPI)
        self.miso_pin = Pin(miso, Pin.ALT_SPI)

        self.height = height
        self.width = width
        self.c_offset = 24
        self.r_offset = 0
        self.flipped = False

        self.draw_buf_size = ceil((width * height) / 8)
        self.draw_buf = array("B", bytes(self.draw_buf_size * [0x00]))
        self.frame_buf = framebuf.FrameBuffer(memoryview(self.draw_buf), width, height, framebuf.MONO_HLSB)

        # Theorhetical max is half of the system frequency (125MHz / 2)
        self.spi = SPI(spi_port, baud, polarity=0, phase=0, firstbit=SPI.MSB, sck=self.sck_pin, mosi=self.mosi_pin, miso=self.miso_pin)

        self.font_cache : array
        self.font_cache_lookup : array
        if cache_font:
            self.font_cache_lookup = array("h", 127 * [0])
            self.build_font_cache()

    def send_command(self, cmd, args = None):
        self.cs_pin.low()
        self.dc_pin.low()
        self.spi.write(bytes([cmd]))
        self.cs_pin.high()
        self.dc_pin.high()

        if args is not None and len(args) > 0:
            self.send_data(bytes(args))

    def send_data(self, data):
        self.cs_pin.low()
        self.spi.write(data)
        self.cs_pin.high()
        self.dc_pin.high()

    def tft_initialize(self):
        self.rt_pin.low()
        time.sleep_ms(100)
        self.rt_pin.high()
        time.sleep_ms(220)

        for cmd in init_cmds:
            self.send_command(cmd[0], None if len(cmd) == 1 else cmd[1:])

    def set_rotation(self, rotation, mirror_x=False, mirror_y=False):
        r = rotation % 4

        flipped = rotation % 2 == 1
        self.c_offset = 24 if not flipped else 0
        self.r_offset = 24 if flipped else 0
        if flipped != self.flipped:
            h = self.height
            self.height = self.width
            self.width = h
            self.flipped = flipped
            self.draw_buf = array("B", bytes(self.draw_buf_size * [0x00]))
            self.frame_buf = framebuf.FrameBuffer(memoryview(self.draw_buf), self.width, self.height, framebuf.MONO_HLSB)

        madctl_arg = (0x00, 0x64, 0xD4, 0xB0)[r]
        if mirror_x:
            madctl_arg = madctl_arg ^ 0x40
        if mirror_y:
            madctl_arg = madctl_arg ^ 0x80
        self.send_command(ST7735_MADCTL, [madctl_arg])

    def set_display_area(self, x, y, w, h):
        # Set column range
        c_offset = self.c_offset
        caset_args = b''.join((
            int16_to_bytes(c_offset + x),
            int16_to_bytes(c_offset + x + w - 1)
        ))
        self.send_command(ST7735_CASET, caset_args)
        # Set row range
        r_offset = self.r_offset
        raset_args = b''.join((
            int16_to_bytes(r_offset + y),
            int16_to_bytes(r_offset + y + h - 1)
        ))
        self.send_command(ST7735_RASET, raset_args)
        # Start memory write
        self.send_command(ST7735_RAMWR)

    # Compose the pixels in the framebuffer into rectangles. Used for faster drawing.
    # Return format is a list of bytes in the format [rect1_x, rect1_y, rect1_w, rect1_h, rect2_x...]
    def find_rects_in_frame(self, start_x, end_x, start_y, end_y):
        # Helper function for checking if a line of pixels can extend down one level
        def can_expand_down(start_x, end_x, y, buf, buf_width):
            #for x in range(start_x, end_x):
            for line_start_x,line_end_x in yield_lines_in_row(buf, buf_width, y, start_x, end_x):
                return line_start_x == start_x and line_end_x == end_x

        def get_expanded_rect(start_x, end_x, y, buf, buf_width):
            h = 1
            next_row = y + 1
            while can_expand_down(start_x, end_x, next_row, buf, buf_width):
                # If it did expand down, unset the pixels expanded
                for exp_x in range(start_x, end_x + 1):
                    set_mono_framebuf_pixel(buf, buf_width, exp_x, next_row, 0)
                next_row += 1
                h += 1
            return (start_x, y, end_x - start_x + 1, h)
    
        buf = memoryview(self.draw_buf)
        buf_width = self.width
        rects = []
        # For each row and column
        for y in range(start_y,end_y+1):
            for line_start_x,line_end_x in yield_lines_in_row(buf, buf_width, y, start_x, end_x):
                rects += get_expanded_rect(line_start_x, line_end_x, y, buf, buf_width)

        return rects
        
    # Draw each ASCII characters 33-126, decompose the characters into rectangles, and cache them for faster drawing
    def build_font_cache(self):
        font_cache_pos = 0
        all_rects = []

        for c in range(127):
            if c < 33:
                self.font_cache_lookup[c] = -1
                continue
            # Get the frame buffer to draw the character
            self.frame_buf.fill_rect(0, 0, 8, 8, 0)
            self.frame_buf.text(chr(c), 0, 0, 1)

            char_rects = self.find_rects_in_frame(0, 7, 0, 7)

            self.font_cache_lookup[c] = font_cache_pos
            len_char_rects = len(char_rects)
            font_cache_pos += len_char_rects + 1
            all_rects += [int(len(char_rects) / 4)] + char_rects

        self.font_cache = array("B", all_rects)

    # Draw the pixels in the region defined in the frame buffer
    def draw_frame_pixels(self, start_x, end_x, start_y, end_y, c, convex=False):
        buf = memoryview(self.draw_buf)
        buf_width = self.width
        c_bytes = int16_to_bytes(c)
        # Gain a few ms by making local function references
        set_display_area = self.set_display_area
        send_data = self.send_data

        for y in range(start_y, end_y + 1):
            for line_start_x,line_end_x in yield_lines_in_row(buf, buf_width, y, start_x, end_x):
                draw_width = line_end_x - line_start_x + 1
                set_display_area(line_start_x, y, draw_width, 1)
                send_data(c_bytes * draw_width)
                if convex:
                    break

    def fill_screen(self, c):
        self.draw_rect(0, 0, self.width, self.height, c)

    def draw_rect(self, x, y, width, height, c, fill=True, thickness=1):
        if fill:
            self.set_display_area(x, y, width, height)
            self.send_data((width * height) * int16_to_bytes(c))
        else:
            self.draw_rect(x, y, width, thickness, c)
            self.draw_rect(x, y + height - thickness, width, thickness, c)
            self.draw_rect(x, y + thickness, thickness, height - (thickness * 2), c)
            self.draw_rect(x + width - thickness, y + thickness, thickness, height - (thickness * 2), c)

    # Draw text pixel by pixel
    def draw_text(self, text, x, y, c):
        text_width = min(8 * len(text), self.width - x)
        text_height = min(8, self.height - y)

        self.frame_buf.fill_rect(x, y, text_width, text_height, 0)
        self.frame_buf.text(text, x, y, 1)
        self.draw_frame_pixels(x, x + text_width, y, y + text_height, c)

    # Draw text using the font cache
    def draw_fast_text(self, text: str, x, y, c):
        x_pos = x
        cache_len = len(self.font_cache_lookup)
        c_bytes = int16_to_bytes(c)

        for symbol in text:
            symbol_ord = ord(symbol)
            if symbol_ord < cache_len:
                # Use the lookup to find where the data for this character is in the font cache
                font_cache_pos = self.font_cache_lookup[symbol_ord]
                if font_cache_pos > -1:
                    # The first byte tells you how many rectangles are in this character
                    num_rects = self.font_cache[font_cache_pos] 
                    for rect in range(num_rects):
                        self.set_display_area(
                            self.font_cache[font_cache_pos + 1] + x_pos, 
                            self.font_cache[font_cache_pos + 2] + y, 
                            self.font_cache[font_cache_pos + 3], 
                            self.font_cache[font_cache_pos + 4])
                        self.send_data(c_bytes * (self.font_cache[font_cache_pos + 3] * self.font_cache[font_cache_pos + 4]))
                        # Advance 4 bytes to the next rectangle
                        font_cache_pos += 4
            x_pos += 8
            if x_pos > self.width:
                return

    def draw_hline(self, x, y, w, c):
        self.draw_rect(x, y, w, 1, c)

    def draw_vline(self, x, y, h, c):
        self.draw_rect(x, y, 1, h, c)

    def draw_line(self, x1, y1, x2, y2, c):
        min_x = min(x1, x2)
        max_x = max(x1, x2)
        min_y = min(y1, y2)
        max_y = max(y1, y2)
        self.frame_buf.fill_rect(min_x, min_y, max_x - min_x, max_y - min_y, 0)
        self.frame_buf.line(x1, y1, x2, y2, 1)
        self.draw_frame_pixels(min_x, max_x, min_y, max_y, c, convex=True)

    def draw_poly(self, x, y, coords, c, fill=True, convex=False):
        coord_array = array("i", coords)
        coord_len = len(coord_array)
        x_max = max([coord_array[i] for i in range(0, coord_len, 2)])
        y_max = max([coord_array[i] for i in range(1, coord_len, 2)])
        self.frame_buf.fill_rect(x, y, x_max - x + 1, y_max - y + 1, 0)
        self.frame_buf.poly(x, y, coord_array, c, fill)
        self.draw_frame_pixels(x, x_max, y, y_max, c, convex)

    def draw_ellipse(self, x, y, rx, ry, c, fill=True):
        # Fill the top-left quadrant and use that to draw the whole shape
        self.frame_buf.fill_rect(x - rx, y - ry, rx, ry, 0)
        self.frame_buf.ellipse(x, y, rx, ry, 1, False, 2)

        buf = memoryview(self.draw_buf)
        buf_width = self.width
        c_bytes = int16_to_bytes(c)
        # For each row and column
        rect_height = ry * 2 if fill else 1
        for buf_y in range(y-ry,y):
            try:
                rect_start_x,rect_end_x = next(yield_lines_in_row(buf, buf_width, buf_y, x-rx, x))
            except StopIteration:
                continue
            rect_width = rect_end_x - rect_start_x + 1
            c_data = c_bytes * (rect_width * rect_height)
            # Draw the left rectangle
            self.set_display_area(rect_start_x, buf_y, rect_width, rect_height)
            self.send_data(c_data)
            # Draw the right rectangle
            self.set_display_area(x + (x - (rect_start_x + rect_width)), buf_y, rect_width, rect_height)
            self.send_data(c_data)

            if fill is False:
                # Draw the left bottom rectangle
                self.set_display_area(rect_start_x, y + (y - buf_y), rect_width, rect_height)
                self.send_data(c_data)
                # Draw the right bottom rectangle
                self.set_display_area(x + (x - (rect_start_x + rect_width)), y + (y - buf_y), rect_width, rect_height)
                self.send_data(c_data)
            else:
                rect_height -= 2

    def draw_svg(self, svg):
        for shape in svg.shapes:
            name = shape.name
            if name is "rect":
                if shape.attributes['fill'] is not None:
                    self.draw_rect(
                        shape.attributes['x'],
                        shape.attributes['y'],
                        shape.attributes['width'],
                        shape.attributes['height'],
                        rgb_to_565(shape.attributes['fill']))
                if shape.attributes['stroke'] is not None:
                    self.draw_rect(
                        shape.attributes['x'],
                        shape.attributes['y'],
                        shape.attributes['width'],
                        shape.attributes['height'],
                        rgb_to_565(shape.attributes['stroke']),
                        fill=False,
                        thickness=shape.attributes['stroke-width'])
            elif name is "circle" or name is "ellipse":
                rx = shape.attributes['rx'] if name is "ellipse" else shape.attributes['r']
                ry = shape.attributes['ry'] if name is "ellipse" else shape.attributes['r']
                if shape.attributes['fill'] is not None:
                    self.draw_ellipse(
                        shape.attributes['cx'], 
                        shape.attributes['cy'], 
                        rx, 
                        ry, 
                        rgb_to_565(shape.attributes['fill']))
                if shape.attributes['stroke'] is not None:
                    self.draw_ellipse(
                        shape.attributes['cx'], 
                        shape.attributes['cy'], 
                        rx, 
                        ry, 
                        rgb_to_565(shape.attributes['stroke']), 
                        False)
            elif name is "line":
                if shape.attributes['stroke'] is not None:
                    self.draw_line(
                        shape.attributes['x1'], 
                        shape.attributes['y1'], 
                        shape.attributes['x2'], 
                        shape.attributes['y2'], 
                        rgb_to_565(shape.attributes['stroke']))
        
        
