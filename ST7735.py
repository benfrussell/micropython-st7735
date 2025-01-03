from machine import Pin, SPI
import time
import framebuf
from array import array
from math import ceil, log2, floor

ST7735_NOP          = const(b'\x00')
ST7735_SWRESET      = const(b'\x01')
ST7735_RDDID        = const(b'\x04')
ST7735_RDDST        = const(b'\x09')
ST7735_SLPIN        = const(b'\x10')
ST7735_SLPOUT       = const(b'\x11')
ST7735_PTLON        = const(b'\x12')
ST7735_NORON        = const(b'\x13')
ST7735_INVOFF       = const(b'\x20')
ST7735_INVON        = const(b'\x21')
ST7735_DISPOFF      = const(b'\x28')
ST7735_DISPON       = const(b'\x29')
ST7735_CASET        = const(b'\x2A')
ST7735_RASET        = const(b'\x2B')
ST7735_RAMWR        = const(b'\x2C')
ST7735_RAMRD        = const(b'\x2E')
ST7735_PTLAR        = const(b'\x30')
ST7735_VSCRDEF      = const(b'\x33')
ST7735_COLMOD       = const(b'\x3A')
ST7735_MADCTL       = const(b'\x36')
ST7735_VSCRSADD     = const(b'\x37')
ST7735_FRMCTR1      = const(b'\xB1')
ST7735_FRMCTR2      = const(b'\xB2')
ST7735_FRMCTR3      = const(b'\xB3')
ST7735_INVCTR       = const(b'\xB4')
ST7735_DISSET5      = const(b'\xB6')
ST7735_PWCTR1       = const(b'\xC0')
ST7735_PWCTR2       = const(b'\xC1')
ST7735_PWCTR3       = const(b'\xC2')
ST7735_PWCTR4       = const(b'\xC3')
ST7735_PWCTR5       = const(b'\xC4')
ST7735_VMCTR1       = const(b'\xC5')
ST7735_RDID1        = const(b'\xDA')
ST7735_RDID2        = const(b'\xDB')
ST7735_RDID3        = const(b'\xDC')
ST7735_RDID4        = const(b'\xDD')
ST7735_PWCTR6       = const(b'\xFC')
ST7735_GMCTRP1      = const(b'\xE0')
ST7735_GMCTRN1      = const(b'\xE1')

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
    [ST7735_MADCTL, 0x08],
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

bitmask = const((128, 64, 32, 16, 8, 4, 2, 1))
bitmask_inv = const((127, 191, 223, 239, 247, 251, 253, 254))

def rgb_to_565(rgb):
    r, g, b = rgb
    # Convert RGB values to 5-6-5 format
    r5 = (r >> 3) & 0x1F  # 5 bits for red
    g6 = (g >> 2) & 0x3F  # 6 bits for green
    b5 = (b >> 3) & 0x1F  # 5 bits for blue
    return (r5 << 11) | (g6 << 5) | b5

class Renderer:
    def draw_rect(self, x, y, w, h, fill, thickness):
        raise NotImplementedError()

    def draw_text(self, text, x, y):
        raise NotImplementedError()

    def draw_hline(self, x, y, w):
        raise NotImplementedError()

    def draw_vline(self, x, y, h):
        raise NotImplementedError()

    def draw_line(self, x1, y1, x2, y2):
        raise NotImplementedError()

    def draw_poly(self, x, y, coords, fill, convex):
        raise NotImplementedError()

    def draw_ellipse(self, x, y, rx, ry, fill):
        raise NotImplementedError()

    def draw_svg(self, svg):
        raise NotImplementedError()

# A mono-only frame buffer built for fast pixel yields
class MonoFrameBuffer(framebuf.FrameBuffer):
    def __init__(self, width: int, height: int):
        self.width = width
        self.draw_buf_size = ceil((width * height) / 8)
        
        self.draw_buf = bytearray(self.draw_buf_size * [0x00])
        self.draw_buf_ref = memoryview(self.draw_buf)
        super().__init__(self.draw_buf_ref, width, height, framebuf.MONO_HLSB)

    def px_in_row(self, y, start_x, end_x):
        buf = self.draw_buf_ref
        buf_width = self.width
        bottom_pos = y * buf_width + start_x
        top_pos = bottom_pos + end_x
        start_byte = floor(bottom_pos / 8)
        pos = start_byte * 8

        for b in buf[start_byte:ceil(top_pos / 8) + 1]:
            while b > 0:
                bitlen = 7 - int(log2(b))
                b = b & bitmask_inv[bitlen]
                new_pos = pos + bitlen
                if new_pos < bottom_pos:
                    continue
                elif new_pos > top_pos:
                    return
                # Yield the x
                yield new_pos % buf_width
            pos += 8

    def lines_in_row(self, y, start_x=0, end_x=None):
        end_x = self.width if None else end_x
        next_x = start_x
        line_width = 0
        for px in self.px_in_row(y, start_x, end_x):
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

    def set_px(self, x, y, p):
        buf = self.draw_buf_ref
        pos = (y * self.width) + x
        mod = pos % 8
        pos = int((pos - mod) / 8)
        if p == 0:
            buf[pos] = buf[pos] & bitmask_inv[mod]
        else:
            buf[pos] = buf[pos] | bitmask[mod]

class Rect(bytearray):
    def __init__(self, x, y, w, h):
        super().__init__((x, y, w, h))

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]

    @property
    def w(self):
        return self[2]

    @property
    def h(self):
        return self[3]
        
        
class MonoFrameBufRenderer(Renderer):
    def __init__(self, width, height, cache_font) -> None:
        self.width = width
        self.height = height
        self.mono_fb = MonoFrameBuffer(self.width, self.height)

        self.font_cache : bytearray
        self.font_cache_lookup : array
        if cache_font:
            self.font_cache_lookup = array("h", 127 * [0])
            self.build_font_cache()

    # Helper function for checking if a line of pixels can extend down one level
    def can_expand_line_down(self, start_x, end_x, y):
        for line_start_x,line_end_x in self.mono_fb.lines_in_row(y, start_x, end_x):
            return line_start_x == start_x and line_end_x == end_x

    def get_expanded_rect(self, start_x, end_x, y) -> Rect:
        can_expand_down = self.can_expand_line_down
        h = 1
        next_row = y + 1
        while can_expand_down(start_x, end_x, next_row):
            # If it did expand down, unset the pixels expanded
            for exp_x in range(start_x, end_x + 1):
                self.mono_fb.set_px(exp_x, next_row, 0)
            next_row += 1
            h += 1
        return Rect(start_x, y, end_x - start_x + 1, h)

    # Compose the pixels in the framebuffer into rectangles. Used for faster drawing.
    # Return format is a list of bytes in the format [rect1_x, rect1_y, rect1_w, rect1_h, rect2_x...]
    def find_rects_in_fb(self, start_x, end_x, start_y, end_y):
        get_expanded_rect = self.get_expanded_rect
        rects = bytearray()
        # For each row and column
        for y in range(start_y,end_y+1):
            for line_start_x,line_end_x in self.mono_fb.lines_in_row(y, start_x, end_x):
                rects.extend(get_expanded_rect(line_start_x, line_end_x, y))
        return rects
        
    # Draw each ASCII characters 33-126, decompose the characters into rectangles, and cache them for faster drawing
    def build_font_cache(self):
        font_cache_pos = 0
        font_cache = bytearray()

        for c in range(127):
            if c < 33:
                self.font_cache_lookup[c] = -1
                continue
            # Get the frame buffer to draw the character
            self.mono_fb.fill_rect(0, 0, 8, 8, 0)
            self.mono_fb.text(chr(c), 0, 0, 1)

            char_rects = self.find_rects_in_fb(0, 7, 0, 7)

            self.font_cache_lookup[c] = font_cache_pos
            len_char_rects = len(char_rects)
            font_cache_pos += len_char_rects + 1
            font_cache += int(len_char_rects / 4).to_bytes(1, 'big')
            font_cache += char_rects
            
        self.font_cache = font_cache

    # Draw the pixels in the region defined in the frame buffer
    def draw_fb_pixels(self, start_x, end_x, start_y, end_y, convex=False):
        rect_buf = bytearray()
        for y in range(start_y, end_y + 1):
            for line_start_x,line_end_x in self.mono_fb.lines_in_row(y, start_x, end_x):
                draw_width = line_end_x - line_start_x + 1
                rect_buf.extend(Rect(line_start_x, y, draw_width, 1))
                if convex:
                    break
        return rect_buf
    
    @staticmethod
    def cull_rect(x, y, w, h, bound_left, bound_top, bound_right, bound_bottom):
        new_x = max(x, bound_left)
        new_y = max(y, bound_top)
        new_w = min(x + w, bound_right) - new_x
        new_h = min(y + h, bound_bottom) - new_y
        return Rect(new_x, new_y, new_w, new_h)

    def draw_rect(self, x, y, w, h, fill=True, thickness=1):
        if fill:
            return bytearray(Rect(x, y, w, h))
        else:
            # Broken
            half_thick = int(thickness / 2)
            width = self.width
            height = self.height
            cull = self.cull_rect

            # Top, left, bottom, right
            return bytearray().join((
                cull(x - half_thick, y - half_thick, thickness, h + thickness, 0, 0, width, height),
                cull(x + half_thick, y - half_thick, w - thickness, thickness, 0, 0, width, height),
                cull(x + w - half_thick, y - half_thick, thickness, h + thickness, 0, 0, width, height),
                cull(x + half_thick, y + h - half_thick, w - thickness, thickness, 0, 0, width, height)
            ))

    # Draw text using the font cache
    def draw_text(self, text: str, x, y):
        x_pos = x
        cache_lookup_len = len(self.font_cache_lookup)
        rect_buf = bytearray()
        cache_ref = memoryview(self.font_cache)
        mono_fb = self.mono_fb
        
        for symbol in text:
            symbol_ord = ord(symbol)
            if symbol_ord < cache_lookup_len:
                # Use the lookup to find where the data for this character is in the font cache
                font_cache_pos = self.font_cache_lookup[symbol_ord]
                if font_cache_pos > -1:
                    # The first byte tells you how many rectangles are in this character
                    num_rects = cache_ref[font_cache_pos]
                    symbol_rects = cache_ref[font_cache_pos + 1:font_cache_pos + 1 + (4 * num_rects)]
                    for r in range(num_rects):
                        symbol_rects[r * 4] += x_pos
                        symbol_rects[r * 4 + 1] += y
                    rect_buf.extend(symbol_rects)
            else:
                mono_fb.fill_rect(x, y, 8, 8, 0)
                mono_fb.text(text, x, y, 1)
                rect_buf.extend(self.draw_fb_pixels(x, x + 8, y, y + 8))

            x_pos += 8
            if x_pos > self.width:
                return rect_buf
        return rect_buf

    def draw_hline(self, x, y, w):
        return memoryview(Rect(x, y, w, 1))

    def draw_vline(self, x, y, h):
        return memoryview(Rect(x, y, 1, h))

    def draw_line(self, x1, y1, x2, y2):
        min_x = min(x1, x2)
        max_x = max(x1, x2)
        min_y = min(y1, y2)
        max_y = max(y1, y2)
        self.mono_fb.fill_rect(min_x, min_y, max_x - min_x, max_y - min_y, 0)
        self.mono_fb.line(x1, y1, x2, y2, 1)
        return self.draw_fb_pixels(min_x, max_x, min_y, max_y, convex=True)

    def draw_poly(self, x, y, coords, fill=True, convex=False):
        coord_array = array("i", coords)
        coord_len = len(coord_array)
        x_max = max([coord_array[i] for i in range(0, coord_len, 2)])
        y_max = max([coord_array[i] for i in range(1, coord_len, 2)])
        self.mono_fb.fill_rect(x, y, x_max - x + 1, y_max - y + 1, 0)
        self.mono_fb.poly(x, y, coord_array, fill)
        return self.draw_fb_pixels(x, x_max, y, y_max, convex)

    def draw_ellipse(self, x, y, rx, ry, fill=True):
        rect_buf = bytearray()
        # Fill the top-left quadrant and use that to draw the whole shape
        self.mono_fb.fill_rect(x - rx, y - ry, rx, ry, 0)
        self.mono_fb.ellipse(x, y, rx, ry, 1, False, 2)
        # For each row and column
        rect_height = ry * 2 if fill else 1
        for buf_y in range(y-ry,y):
            try:
                rect_start_x,rect_end_x = next(self.mono_fb.lines_in_row(buf_y, x-rx, x))
            except StopIteration:
                continue
            rect_width = rect_end_x - rect_start_x + 1
            # Draw the left rectangle
            rect_buf.extend(Rect(rect_start_x, buf_y, rect_width, rect_height))
            rect_buf.extend(Rect(x + (x - (rect_start_x + rect_width)), buf_y, rect_width, rect_height))

            if fill is False:
                # Draw the left bottom rectangle
                rect_buf.extend(Rect(rect_start_x, y + (y - buf_y), rect_width, rect_height))
                rect_buf.extend(Rect(x + (x - (rect_start_x + rect_width)), y + (y - buf_y), rect_width, rect_height))
            else:
                rect_height -= 2
        return rect_buf

    def draw_svg(self, svg):
        data = []
        for shape in svg.shapes:
            name = shape.name
            if name is "rect":
                if 'fill' in shape.attributes and shape.attributes['fill'] is not None:
                    data.append((
                        rgb_to_565(shape.attributes['fill']), 
                        Rect(
                            shape.attributes['x'],
                            shape.attributes['y'],
                            shape.attributes['width'],
                            shape.attributes['height']
                        )
                    ))
                if 'stroke' in shape.attributes and shape.attributes['stroke'] is not None:
                    data.append((
                        rgb_to_565(shape.attributes['stroke']),
                        self.draw_rect(
                            shape.attributes['x'], 
                            shape.attributes['y'],
                            shape.attributes['width'],
                            shape.attributes['height'],
                            fill=False,
                            thickness=shape.attributes['stroke-width']
                        )
                    ))
            elif name is "circle" or name is "ellipse":
                rx = shape.attributes['rx'] if name is "ellipse" else shape.attributes['r']
                ry = shape.attributes['ry'] if name is "ellipse" else shape.attributes['r']
                if 'fill' in shape.attributes and shape.attributes['fill'] is not None:
                    data.append((
                        rgb_to_565(shape.attributes['fill']),
                        self.draw_ellipse(
                            shape.attributes['cx'], 
                            shape.attributes['cy'], 
                            rx, 
                            ry
                        )
                    ))
                if 'stroke' in shape.attributes and shape.attributes['stroke'] is not None:
                    data.append((
                        rgb_to_565(shape.attributes['stroke']),
                        self.draw_ellipse(
                            shape.attributes['cx'], 
                            shape.attributes['cy'], 
                            rx, 
                            ry, 
                            False
                        )
                    ))
            elif name is "line":
                if 'stroke' in shape.attributes and shape.attributes['stroke'] is not None:
                    data.append((
                        rgb_to_565(shape.attributes['stroke']),
                        self.draw_line(
                            shape.attributes['x1'], 
                            shape.attributes['y1'], 
                            shape.attributes['x2'], 
                            shape.attributes['y2']
                        )
                    ))
        return data
        
class ST7735:
    def __init__(self, dc, cs, rt, sck, mosi, miso, spi_port, baud=62_500_000, height=160, width=80, cache_font=True, renderer: Renderer | None = None):
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

        # Theorhetical max is half of the system frequency (125MHz / 2)
        self.spi = SPI(spi_port, baud, polarity=0, phase=0, firstbit=SPI.MSB, sck=self.sck_pin, mosi=self.mosi_pin, miso=self.miso_pin)
        if renderer is None:
            self.renderer = MonoFrameBufRenderer(width, height, cache_font)
        else:
            self.renderer = renderer

    def send_command(self, cmd : bytes, args : bytes | None = None):
        cs_pin = self.cs_pin
        dc_pin = self.dc_pin
        spi = self.spi

        cs_pin.low()
        dc_pin.low()
        spi.write(cmd)
        cs_pin.high()
        dc_pin.high()

        if args is not None and len(args) > 0:
            cs_pin.low()
            spi.write(args)
            cs_pin.high()
            dc_pin.high()

    def tft_initialize(self):
        send_cmd = self.send_command
        self.rt_pin.low()
        time.sleep_ms(100)
        self.rt_pin.high()
        time.sleep_ms(220)

        for cmd in init_cmds:
            send_cmd(cmd[0], None if len(cmd) == 1 else bytes(cmd[1:]))

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
            # self.draw_buf = array("B", bytes(self.draw_buf_size * [0x00]))
            # self.frame_buf = framebuf.FrameBuffer(memoryview(self.draw_buf), self.width, self.height, framebuf.MONO_HLSB)

        madctl_arg = (0x08, 0x6C, 0xDC, 0xB8)[r]
        if mirror_x:
            madctl_arg = madctl_arg ^ 0x40
        if mirror_y:
            madctl_arg = madctl_arg ^ 0x80
        self.send_command(ST7735_MADCTL, bytes(madctl_arg))

    def send_rects(self, data: bytes, c: bytes):
        # Local copy of functions for performance
        c_offset = self.c_offset
        r_offset = self.r_offset
        send_cmd = self.send_command
        cs_pin = self.cs_pin
        dc_pin = self.dc_pin
        size = len(data)
        i = 0

        while i < size:
            x = data[i]
            y = data[i + 1]
            w = data[i + 2]
            h = data[i + 3]
            caset_args = bytes((
                ((c_offset + x) >> 8) & 0xFF,
                (c_offset + x) & 0xFF,
                ((c_offset + x + w - 1) >> 8) & 0xFF,
                (c_offset + x + w - 1) & 0xFF
            ))
            send_cmd(ST7735_CASET, caset_args)
            # Set row range
            
            raset_args = bytes((
                ((r_offset + y) >> 8) & 0xFF,
                (r_offset + y) & 0xFF,
                ((r_offset + y + h - 1) >> 8) & 0xFF,
                (r_offset + y + h - 1) & 0xFF
            ))
            send_cmd(ST7735_RASET, raset_args)
            # Start memory write
            send_cmd(ST7735_RAMWR)

            cs_pin.low()
            self.spi.write(c * (w * h))
            cs_pin.high()
            dc_pin.high()
            i += 4

    def fill_screen(self, c: bytes):
        self.send_rects(bytes((0, 0, self.width, self.height)), c)

    def draw_rect(self, x, y, w, h, c: bytes, fill=True, thickness=1):
        self.send_rects(self.renderer.draw_rect(x, y, w, h, fill, thickness), c)

    def draw_text(self, text, x, y, c: bytes):
        self.send_rects(self.renderer.draw_text(text, x, y), c)

    def draw_hline(self, x, y, w, c: bytes):
        self.send_rects(self.renderer.draw_hline(x, y, w), c)

    def draw_vline(self, x, y, h, c: bytes):
        self.send_rects(self.renderer.draw_vline(x, y, h), c)

    def draw_line(self, x1, y1, x2, y2, c: bytes):
        self.send_rects(self.renderer.draw_line(x1, y1, x2, y2), c)

    def draw_poly(self, x, y, coords, c: bytes, fill=True, convex=False):
        self.send_rects(self.renderer.draw_poly(x, y, coords, fill, convex), c)

    def draw_ellipse(self, x, y, rx, ry, c: bytes, fill = True):
        self.send_rects(self.renderer.draw_ellipse(x, y, rx, ry, fill), c)

    def draw_svg(self, svg):
        for c, b in self.renderer.draw_svg(svg):
            self.send_rects(b, c)
        
        
