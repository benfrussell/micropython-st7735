class Tag:
    def __init__(self, name, attributes):
        self.name = name
        self.attributes = attributes

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
        self._tags = []
        self._tag = ""
        self._attrs = dict()
        self._attr_name = ""
        self._attr_value = True
        self._val_quote_type = ""
        self._stage = self.ReadingStage["BEFORE_TAG"]

    def _finish_tag(self):
        if self._tag[0] is "_" or self._tag[0].isalpha():
            self._tags.append(Tag(self._tag, self._attrs))
        self._tag = ""
        self._attrs = dict()
        self._stage = self.ReadingStage["BEFORE_TAG"]

    def _finish_attr(self):
        self._attrs[self._attr_name] = self._attr_value
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

    def get_all_tags(self, stream):
        self._stage = self.ReadingStage["BEFORE_TAG"]
        self._tags = []
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
                    self._finish_tag()
                else:
                    self._tag += char

            elif self._stage == 2: # BEFORE_ATTR
                if char.isalpha() or char == '_':
                    self._goto_reading_attr(char)
                elif char is '>':
                    self._finish_tag()

            elif self._stage == 3: # READING_ATTR
                if char.isspace():
                    self._goto_finished_attr()
                elif char is '=':
                    self._goto_before_val()
                elif char is '>':
                    self._finish_attr()
                    self._finish_tag()
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
                    self._finish_tag()
                    
            elif self._stage == 5: # BEFORE_VAL
                if char is '"' or char is "'":
                    self._goto_reading_val(char)

            elif self._stage == 6: # READING_VAL
                if char is self._val_quote_type:
                    self._finish_attr()
                    self._goto_before_attr()
                else:
                    self._attr_value += char
        return self._tags