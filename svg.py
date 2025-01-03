from array import array

try:
    import colours
except ImportError:
    colours = None 

class Element:
    def __init__(self, name, attributes):
        self.name = name
        self.attributes = attributes

class SVG:
    ValidElements = ("rect", "circle", "ellipse", "line", "polyline", "polygon")
    # Define a dictionary to map SVG units to their pixel values
    UnitsToPixels = {
        "px": 1,
        "mm": 3.77953,
        "cm": 37.79528,
        "q": 0.94488,
        "in": 96,
        "pc": 16,
        "pt": 1.33333
    }
    
    def __init__(self, shapes=[]):
        self.shapes = shapes

    @staticmethod
    def colour_to_rgb(colour_str: str):
        def hsl_to_rgb(h, s, l):
            c = (1 - abs(2 * l - 1)) * s
            h_ = h / 60
            x = c * (1 - abs(h_ % 2 - 1))
            m = l - c / 2

            r, g, b = 0, 0, 0
            if 0 <= h_ < 1:
                r, g, b = c, x, 0
            elif 1 <= h_ < 2:
                r, g, b = x, c, 0
            elif 2 <= h_ < 3:
                r, g, b = 0, c, x
            elif 3 <= h_ < 4:
                r, g, b = 0, x, c
            elif 4 <= h_ < 5:
                r, g, b = x, 0, c
            elif 5 <= h_ <= 6:
                r, g, b = c, 0, x

            r = int((r + m) * 255)
            g = int((g + m) * 255)
            b = int((b + m) * 255)
            
            return r, g, b
        
        def hex_to_rgb(hex_colour):
            # Remove the '#' symbol if it exists
            hex_colour = hex_colour.lstrip('#')
            
            # Convert the hex color to an RGB tuple
            r = int(hex_colour[0:2], 16)
            g = int(hex_colour[2:4], 16)
            b = int(hex_colour[4:6], 16)
            
            return (r, g, b)

        colour_str = colour_str.strip().lower()

        if colour_str.startswith("#"):
            return hex_to_rgb(colour_str)

        elif colour_str.startswith("rgb"):
            colour_str = colour_str[colour_str.index("(") + 1:].strip('()')
            vals = [v.strip() for v in colour_str.split(',')[:3]]
            return tuple(int(val) if "%" not in val else float(val.strip("%")) * 2.55 for val in vals)

        elif colour_str.startswith("hsl"):
            colour_str = colour_str[colour_str.index("(") + 1:].strip('()')
            vals = [v.strip() for v in colour_str.split(',')[:3]]
            return hsl_to_rgb(float(vals[0]), float(vals[1].strip("%")) / 100, float(vals[2].strip("%")) / 100)
            
        elif hasattr(colours, colour_str.upper()):
            return getattr(colours, colour_str.upper())

        return None
    
    @staticmethod
    def length_to_pixels(length_string: str):
        # Split the length string into the numeric value and the unit
        length_string = length_string.strip().lower()
        value = ''.join([c if c.isdigit() or c is '.' else '' for c in length_string])
        unit = length_string.replace(value, '')

        try:
            value = float(value)
        except ValueError:
            raise ValueError(f"Invalid numeric value in SVG length: '{value}'")
        
        if unit is '':
            return int(value)
        elif unit not in SVG.UnitsToPixels.keys():
            raise ValueError(f"Unsupported SVG unit: '{unit}'")

        return int(value * SVG.UnitsToPixels[unit])

    @staticmethod
    def read_svg(stream):
        reader = SimpleXMLReader()
        elements = reader.get_all_elements(stream)
        shapes = []
        for e in elements:
            if e.name not in SVG.ValidElements:
                continue

            for attr,val in e.attributes.items():
                if attr in ("fill", "stroke"):
                    e.attributes[attr] = SVG.colour_to_rgb(val)
                elif 'x' in attr or 'y' in attr or attr in ("width", "height", "r", "stroke-width"):
                    e.attributes[attr] = SVG.length_to_pixels(val)

            shapes.append(e)
        return SVG(shapes)

class SimpleXMLReader:
    ReadingStage = {
        "BEFORE_TAG":       0, # Looking for < (-> reading tag)
        "READING_TAG":      1, # Looking for space (-> before attr) or > (-> finish tag)
        "BEFORE_ATTR":      2, # Looking for _ or letter (-> reading attr) or > (-> finish tag)
        "READING_ATTR":     3, # Looking for space (-> finish attr) or = (-> before val) or > (-> finish tag)
        "FINISHED_ATTR":    4, # Looking for _ or letter (-> reading attr) or = (-> before val) or > (-> finish tag)
        "BEFORE_VAL":       5, # Looking for " or ' (-> reading val)
        "READING_VAL":      6  # Looking for matching " or ' (-> before attr)
    }

    def __init__(self):
        self._elements = []
        self._tag = ""
        self._attrs = dict()
        self._attr_name = ""
        self._attr_value = True
        self._val_quote_type = ""
        self._stage = self.ReadingStage["BEFORE_TAG"]

    def _finish_element(self):
        if self._tag[0] is "_" or self._tag[0].isalpha():
            self._elements.append(Element(self._tag.lower(), self._attrs))
        self._tag = ""
        self._attrs = dict()
        self._stage = self.ReadingStage["BEFORE_TAG"]

    def _finish_attr(self):
        self._attrs[self._attr_name.lower()] = self._attr_value
        self._attr_name = ""
        self._attr_value = True

    def _goto_reading_tag(self):
        self._tag = ""
        self._stage = self.ReadingStage["READING_TAG"]

    def _goto_before_attr(self):
        self._stage = self.ReadingStage["BEFORE_ATTR"]

    def _goto_reading_attr(self, first_char):
        self._attr_name = first_char
        self._stage = self.ReadingStage["READING_ATTR"]

    def _goto_finished_attr(self):
        self._stage = self.ReadingStage["FINISHED_ATTR"]

    def _goto_before_val(self):
        self._val_quote_type = ""
        self._stage = self.ReadingStage["BEFORE_VAL"]

    def _goto_reading_val(self, quote_type):
        self._val_quote_type = quote_type
        self._attr_value = ""
        self._stage = self.ReadingStage["READING_VAL"]

    def get_all_elements(self, stream):
        self._stage = self.ReadingStage["BEFORE_TAG"]
        self._elements = []
        while True:
            char = stream.read(1)
            if not char:
                break
            
            if self._stage == 0: # BEFORE_TAG
                if char is '<':
                    self._goto_reading_tag()
            elif self._stage == 1: # READING_TAG
                if char.isspace():
                    self._goto_before_attr()
                elif char is '>':
                    self._finish_element()
                else:
                    self._tag += char

            elif self._stage == 2: # BEFORE_ATTR
                if char.isalpha() or char == '_':
                    self._goto_reading_attr(char)
                elif char is '>':
                    self._finish_element()

            elif self._stage == 3: # READING_ATTR
                if char.isspace():
                    self._goto_finished_attr()
                elif char is '=':
                    self._goto_before_val()
                elif char is '>':
                    self._finish_attr()
                    self._finish_element()
                else:
                    self._attr_name += char

            elif self._stage == 4: # FINISHED_ATTR
                if char is '=':
                    self._goto_before_val()
                elif char.isalpha() or char == '_':
                    self._finish_attr()
                    self._goto_reading_attr(char)
                elif char is '>':
                    self._finish_attr()
                    self._finish_element()
                    
            elif self._stage == 5: # BEFORE_VAL
                if char is '"' or char is "'":
                    self._goto_reading_val(char)

            elif self._stage == 6: # READING_VAL
                if char is self._val_quote_type:
                    self._finish_attr()
                    self._goto_before_attr()
                else:
                    self._attr_value += char
        return self._elements
    
def int16_to_bytes(i: int):
    return bytes([(i >> 8) & 0xFF, i & 0xFF])
    
class CachedSVG:
    def __init__(self):
        self.rects = array("B", bytes())
        self._rects_buffer = []
        self._new_rect_data = []
        self._new_rect_num = 0
        self._colour = int16_to_bytes(0x0000)

    def add_rect(self, x, y, w, h, c: bytes):
        if c != self._colour:
            if self._new_rect_num > 0:
                self._add_rects_to_buffer()
            self._colour = c
        self._new_rect_data.extend([x, y, w, h])
        self._new_rect_num += 1

    def finish_caching(self):
        self._add_rects_to_buffer()
        self.rects = array("B", self._rects_buffer)
        self._rects_buffer = []

    def _add_rects_to_buffer(self):
        for i in range(0, self._new_rect_num, 255):
            self._rects_buffer.extend([self._colour[0], self._colour[1], min(255, self._new_rect_num - i)])
            self._rects_buffer.extend(self._new_rect_data)
        self._new_rect_data = []
        self._new_rect_num = 0


def create_cached_svg(self, svg):
    cached_svg = CachedSVG()
    self._draw_to_cache = cached_svg
    self.draw_svg(svg)
    cached_svg.finish_caching()
    self._draw_to_cache = None
    return cached_svg
    
def draw_cached_svg(self, cached_svg: CachedSVG, x = 0, y = 0):
    i = 0
    last_index = len(cached_svg.rects) - 1
    while i < last_index:
        c = bytes(cached_svg.rects[i:i+2])
        num_rects = cached_svg.rects[i + 2]
        i += 3
        for _ in range(num_rects):
            self.draw_rect(
                cached_svg.rects[i] + x, 
                cached_svg.rects[i + 1] + y, 
                cached_svg.rects[i + 2], 
                cached_svg.rects[i + 3],
                c)
            i += 4