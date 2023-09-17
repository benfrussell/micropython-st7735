SVGColours = {
    "aliceblue": 0xF7DF,        "antiquewhite": 0xFD5A,         "aqua": 0x07FF,                 "aquamarine": 0x7FFA,       
    "azure": 0xF7FF,            "beige": 0xF7BB,                "bisque": 0xFF38,               "black": 0x0000,        
    "blanchedalmond": 0xFF59,   "blue": 0x001F,                 "blueviolet": 0x895C,           "brown": 0xA145,            
    "burlywood": 0xDDD0,        "cadetblue": 0x5CF4,            "chartreuse": 0x7FE0,           "chocolate": 0xD344,
    "coral": 0xFF3A,            "cornflowerblue": 0x64BD,       "cornsilk": 0xFFDB,             "crimson": 0xD8A7,
    "cyan": 0x07FF,             "darkblue": 0x0011,             "darkcyan": 0x0451,             "darkgoldenrod": 0xBC21,
    "darkgray": 0xAD55,         "darkgreen": 0x0320,            "darkgrey": 0xAD55,             "darkkhaki": 0xBDAD,
    "darkmagenta": 0x8811,      "darkolivegreen": 0x5345,       "darkorange": 0xFC60,           "darkorchid": 0x9999,
    "darkred": 0x8800,          "darksalmon": 0xECAF,           "darkseagreen": 0x8DF1,         "darkslateblue": 0x49F1,
    "darkslategray": 0x2A69,    "darkslategrey": 0x2A69,        "darkturquoise": 0x067A,        "darkviolet": 0x901A,
    "deeppink": 0xF8B2,         "deepskyblue": 0x05FF,          "dimgray": 0x6B4D,              "dimgrey": 0x6B4D,
    "dodgerblue": 0x1C9F,       "firebrick": 0xB104,            "floralwhite": 0xFFDE,          "forestgreen": 0x2444,
    "fuchsia": 0xF81F,          "gainsboro": 0xDEFB,            "ghostwhite": 0xFFDF,           "gold": 0xFEA0,
    "goldenrod": 0xDD24,        "gray": 0x8410,                 "grey": 0x8410,                 "green": 0x0400,
    "greenyellow": 0xAFE5,      "honeydew": 0xF7FE,             "hotpink": 0xFB56,              "indianred": 0xCAEB,
    "indigo": 0x4810,           "ivory": 0xFFFE,                "khaki": 0xF731,                "lavender": 0xE73F,
    "lavenderblush": 0xFF9E,    "lawngreen": 0x7FE0,            "lemonchiffon": 0xFFD9,         "lightblue": 0xAEDC,
    "lightcoral": 0xF410,       "lightcyan": 0xE7FF,            "lightgoldenrodyellow": 0xFFFC, "lightgray": 0xD69A,
    "lightgreen": 0x9772,       "lightgrey": 0xD69A,            "lightpink": 0xFD19,            "lightsalmon": 0xFD0F,
    "lightseagreen": 0x2595,    "lightskyblue": 0x867F,         "lightslategray": 0x7453,       "lightslategrey": 0x7453,
    "lightsteelblue": 0xB63B,   "lightyellow": 0xFFFC,          "lime": 0x07E0,                 "limegreen": 0x3666,
    "linen": 0xF77C,            "magenta": 0xF81F,              "maroon": 0x8000,               "mediumaquamarine": 0x6675,
    "mediumblue": 0x0019,       "mediumorchid": 0xBABA,         "mediumpurple": 0x939B,         "mediumseagreen": 0x3D8E,
    "mediumslateblue": 0x7B5D,  "mediumspringgreen": 0x07D3,    "mediumturquoise": 0x4E99,      "mediumvioletred": 0xC0B0,
    "midnightblue": 0x18CE,     "mintcream": 0xF7FF,            "mistyrose": 0xFF3E,            "moccasin": 0xFF36,
    "navajowhite": 0xFFDE,      "navy": 0x0010,                 "oldlace": 0xFFE3,              "olive": 0x8400,
    "olivedrab": 0x6C64,        "orange": 0xFD20,               "orangered": 0xFA20,            "orchid": 0xDB9A,
    "palegoldenrod": 0xEF55,    "palegreen": 0x9FD3,            "paleturquoise": 0xAF7D,        "palevioletred": 0xDB92,
    "papayawhip": 0xFF7A,       "peachpuff": 0xFED7,            "peru": 0xCC27,                 "pink": 0xFE19,
    "plum": 0xDD1B,             "powderblue": 0xB71C,           "purple": 0x8010,               "rebeccapurple": 0x6633,
    "red": 0xF800,              "rosybrown": 0xBC71,            "royalblue": 0x435C,            "saddlebrown": 0x8A22,
    "salmon": 0xFC0E,           "sandybrown": 0xF52C,           "seagreen": 0x2C4A,             "seashell": 0xFFBD,
    "sienna": 0xA285,           "silver": 0xC618,               "skyblue": 0x867D,              "slateblue": 0x6AD9,
    "slategray": 0x7412,        "slategrey": 0x7412,            "snow": 0xFFDF,                 "springgreen": 0x07EF,
    "steelblue": 0x4416,        "tan": 0xD5B1,                  "teal": 0x0410,                 "thistle": 0xDDFB,
    "tomato": 0xFB08,           "turquoise": 0x471A,            "violet": 0xEC1D,               "wheat": 0xF6F6,
    "white": 0xFFFF,            "whitesmoke": 0xF7BE,           "yellow": 0xFFE0,               "yellowgreen": 0x9E66,
}


class Element:
    def __init__(self, name, attributes):
        self.name = name
        self.attributes = attributes

class SVG:
    ValidElements = ("rect", "circle", "ellipse", "line", "polyline", "polygon")
    def __init__(self, shapes=[]):
        self.shapes = shapes

    @staticmethod
    def colour_to_hex(colour_str: str):
        def rgb_to_hex(rgb):
            r = int(rgb[0] * 31)
            g = int(rgb[1] * 63)
            b = int(rgb[2] * 31)
            return (r << 11) | (g << 5) | b

        def hsl_to_hex(hsl):
            h, s, l = hsl
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
            elif 5 <= h_ < 6:
                r, g, b = c, 0, x

            r = int((r + m) * 255)
            g = int((g + m) * 255)
            b = int((b + m) * 255)

            r = int(r * 31 / 255)
            g = int(g * 63 / 255)
            b = int(b * 31 / 255)

            return (r << 11) | (g << 5) | b

        colour_str = colour_str.strip().lower()

        if colour_str.startswith("rgb"):
            colour_str = colour_str[colour_str.index("(") + 1:].strip('()')
            rgb_values = [float(val) / 255 if "%" not in val else float(val.strip("%")) / 100 for val in colour_str.split(',')[:3]]
            if len(rgb_values) == 3:
                return rgb_to_hex(rgb_values)

        elif colour_str.startswith("hsl"):
            colour_str = colour_str[colour_str.index("(") + 1:].strip('()')
            hsl_values = [float(val) if "%" not in val else float(val.strip("%")) / 100 for val in colour_str.split(',')[:3]]
            if len(hsl_values) == 3:
                return hsl_to_hex(hsl_values)
            
        elif colour_str in SVGColours.keys():
            return SVGColours[colour_str]

        return None

    @staticmethod
    def read_svg(stream):
        reader = SimpleXMLReader()
        elements = reader.get_all_elements(stream)
        shapes = []
        for e in elements:
            if e.name not in SVG.ValidElements:
                continue
            attrs = e.attributes.keys()
            if "fill" in attrs:
                e.attributes["fill"] = SVG.colour_to_hex(e.attributes["fill"])
            if "stroke" in attrs:
                e.attributes["stroke"] = SVG.colour_to_hex(e.attributes["stroke"])
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