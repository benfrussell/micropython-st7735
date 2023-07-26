from machine import Pin, SPI
import time
import framebuf
from array import array
from math import ceil
import gc

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
ST7735_MADCTL_MY    = const(0x80)
ST7735_MADCTL_MX    = const(0x40)
ST7735_MADCTL_MV    = const(0x20)
ST7735_MADCTL_ML    = const(0x10)
ST7735_MADCTL_RGB   = const(0x00)
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
    # MADCTL - Sets row/column address order, RGB order, refresh order
    [ST7735_MADCTL, 0xc0],
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

bitmask = const((128, 64, 32, 16, 8, 4, 2, 1))

def get_mono_framebuf_pixel(framebuf, buf_width, x, y):
    pos = (y * buf_width) + x
    mod = pos % 8
    pos = int((pos - mod) / 8)
    return (framebuf[pos] & bitmask[mod]) > 0


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

        gc.collect()
        mem = gc.mem_free()
        self.draw_buf_size = ceil((width * height) / 8)
        self.draw_buf = array("B", bytes(self.draw_buf_size * [0x00]))
        self.frame_buf = framebuf.FrameBuffer(memoryview(self.draw_buf), width, height, framebuf.MONO_HLSB)
        gc.collect()
        print(f"Frame buf size: {mem - gc.mem_free()} bytes")

        # Theorhetical max is half of the system frequency (125MHz / 2)
        self.spi = SPI(spi_port, baud, polarity=0, phase=0, firstbit=SPI.MSB, sck=self.sck_pin, mosi=self.mosi_pin, miso=self.miso_pin)

        gc.collect()
        mem = gc.mem_free()
        self.font_cache : array
        self.font_cache_lookup : array
        if cache_font:
            self.font_cache_lookup = array("h", 127 * [0])
            self.build_font_cache()
        gc.collect()
        print(f"Cache size: {mem - gc.mem_free()} bytes")

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

        start = time.ticks_ms()
        for cmd in init_cmds:
            self.send_command(cmd[0], None if len(cmd) == 1 else cmd[1:])
        print(f"Init time: {time.ticks_diff(time.ticks_ms(), start)} ms")

    def set_display_area(self, x, y, w, h):
        # Set column range
        caset_args = b''.join((
            int16_to_bytes(24 + x),
            int16_to_bytes(24 + x + w - 1)
        ))
        self.send_command(ST7735_CASET, caset_args)
        # Set row range
        raset_args = b''.join((
            int16_to_bytes(0 + y),
            int16_to_bytes(0 + y + h - 1)
        ))
        self.send_command(ST7735_RASET, raset_args)
        # Start memory write
        self.send_command(ST7735_RAMWR)

    def fill_screen(self, colour):
        self.fill_rectangle(0, 0, self.width, self.height, colour)

    def fill_rectangle(self, x, y, width, height, colour):
        self.set_display_area(x, y, width, height)
        self.send_data(bytes((width * height) * int16_to_bytes(colour)))

    # Decomposes the pixels in the framebuffer into rectangles. Used for faster drawing.
    # Return format is a list of bytes in the format [rect1_x, rect1_y, rect1_w, rect1_h, rect2_x...]
    def find_rects_in_frame(self, start_x, end_x, start_y, end_y):
        # Helper function for checking if a line of pixels can extend down one level
        def can_expand_down(start_x, end_x, y, buf, buf_width):
            can_expand = True
            for x in range(start_x, end_x):
                if get_mono_framebuf_pixel(buf, buf_width, x, y) is False:
                    can_expand = False     
                    break
            return can_expand
    
        buf = memoryview(self.draw_buf)
        buf_width = self.width
        visited = []
        visited_pos = 0
        rects = []
        # For each row and column
        for buf_y in range(start_y,end_y+1):
            rect_width = 0
            rect_height = 1
            visited_pos = buf_y * buf_width
            for buf_x in range(start_x,end_x+1):
                # If the pixel is filled and hasn't been visited yet, expand right by one
                if visited_pos not in visited and get_mono_framebuf_pixel(buf, buf_width, buf_x, buf_y):
                    rect_width += 1
                # If the pixel was not filled or was visited, and we have identified a filled area (width > 0)
                elif rect_width > 0:
                    # See how far we can expand down at the position with this width
                    rect_start_x = buf_x - rect_width
                    next_row = buf_y + rect_height
                    while can_expand_down(rect_start_x, buf_x, next_row, buf, buf_width):
                        # If it did expand down, add all of the positions of pixels that were expanded to into the visited list
                        visited += range((next_row * buf_width) + rect_start_x, (next_row * buf_width) + buf_x)
                        next_row += 1
                        rect_height += 1

                    rects += (rect_start_x, buf_y, rect_width, rect_height)
                    rect_width = 0
                    rect_height = 1
                visited_pos += 1

        return rects
        
    # Draw each ASCII characters 33-126, decompose the characters into rectangles, and cache them for faster drawing
    def build_font_cache(self):
        start = time.ticks_ms()
        font_cache_pos = 0
        all_rects = []

        for c in range(33,127):
            if c < 33:
                self.font_cache_lookup[c] = -1
            # Get the frame buffer to draw the character
            self.frame_buf.fill_rect(0, 0, 8, 8, 0)
            self.frame_buf.text(chr(c), 0, 0, 1)

            char_rects = self.find_rects_in_frame(0, 7, 0, 7)

            self.font_cache_lookup[c] = font_cache_pos
            len_char_rects = len(char_rects)
            font_cache_pos += len_char_rects + 1
            all_rects += [int(len(char_rects) / 4)] + char_rects

        self.font_cache = array("B", all_rects)
        print(f"Cache time: {time.ticks_diff(time.ticks_ms(), start)} ms")

    # Draw the pixels in the region defined in the frame buffer
    def draw_frame_buffer(self, start_x, end_x, start_y, end_y, colour):
        buf = memoryview(self.draw_buf)
        buf_width = self.width
        colour_bytes = bytes(int16_to_bytes(colour))
        # Gain a few ms by making local function references
        get_pixel = get_mono_framebuf_pixel
        set_display_area = self.set_display_area
        send_data = self.send_data
        
        for draw_y in range(start_y, end_y):
            draw_width = 0
            for draw_x in range(start_x, end_x):
                if get_pixel(buf, buf_width, draw_x, draw_y):
                    draw_width += 1
                elif draw_width > 0:
                    set_display_area(draw_x - draw_width, draw_y, draw_width, 1)
                    send_data(colour_bytes * draw_width)
                    draw_width = 0
    
    # Draw text pixel by pixel
    def draw_text(self, text, x, y, colour):
        text_width = min(8 * len(text), self.width - x)
        text_height = min(8, self.height - y)

        self.frame_buf.fill_rect(x, y, text_width, text_height, 0)
        self.frame_buf.text(text, x, y, 1)
        self.draw_frame_buffer(x, x + text_width, y, y + text_height, colour)

    # Draw text using the font cache
    def draw_fast_text(self, text: str, x, y, colour):
        x_pos = x
        cache_len = len(self.font_cache_lookup)
        colour_bytes = bytes(int16_to_bytes(colour))

        for symbol in text:
            symbol_ord = ord(symbol)
            if symbol_ord < cache_len:
                # Use the lookup to find where the data for this character is in the font cache
                font_cache_pos = self.font_cache_lookup[symbol_ord]
                # The first byte tells you how many rectangles are in this character
                num_rects = self.font_cache[font_cache_pos] 
                for rect in range(num_rects):
                    # Unpack the rectangle data from the font cache
                    rx = self.font_cache[font_cache_pos + 1]
                    ry = self.font_cache[font_cache_pos + 2]
                    rw = self.font_cache[font_cache_pos + 3]
                    rh = self.font_cache[font_cache_pos + 4] 
                    self.set_display_area(x_pos + rx, y + ry, rw, rh)
                    self.send_data(colour_bytes * (rw * rh))
                    # Advance 4 bytes to the next rectangle
                    font_cache_pos += 4

            x_pos += 8
            if x_pos > self.width:
                return


