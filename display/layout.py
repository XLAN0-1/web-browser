from uris.http_uri import Text, Tag
import tkinter.font
import sys
sys.path.append("..")

from cache import fonts_cache


HSTEP, VSTEP = 13, 18
WIDTH, HEIGHT = 1500, 1000

class Layout:
    def __init__(self, tokens):
        self.font_cache = fonts_cache.FontsCache()
        self.display_list = []
        self.line = []
        self.cursor_x = HSTEP
        self.cursor_y = VSTEP
        self.weight = "normal"
        self.style = "roman"
        self.size = 16
        self.width = WIDTH
        self.tokens = tokens

        for tok in tokens:
            self.token(tok)

        self.flush()

    def get_display_list(self, width, height):
        self.width = width
        self.height = height

        for tok in self.tokens:
            self.token(tok)
        

    def token(self, tok):
        if isinstance(tok, Text):
            for word in tok.text.split():
                self.word(word)
        elif tok.tag == "i":
            self.style = "italic"
        elif tok.tag == "/i":
            self.style = "roman"
        elif tok.tag == "b":
            self.weight = "bold"
        elif tok.tag == "/b":
            self.weight = "normal"
        elif tok.tag == "small":
            self.size -= 2
        elif tok.tag == "/small":
            self.size += 2
        elif tok.tag == "big":
            self.size += 4
        elif tok.tag == "/big":
            self.size -= 4
        elif tok.tag == "br":
            self.flush()
        elif tok.tag == "/p":
            self.flush()
            self.cursor_y += VSTEP

    def word(self, word):
        font = self.font_cache.get_font(self.size, self.weight, self.style)
        
        w = font.measure(word)


        if self.cursor_x + w >= self.width - HSTEP:
            self.flush()
            self.cursor_y += font.metrics("linespace") * 1.25

        self.line.append((self.cursor_x, word, font))
        self.cursor_x += w + font.measure(" ")
       
        

    def flush(self):
        if not self.line: return
        metrics = [font.metrics() for x, word, font in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])

        baseline = self.cursor_y + 1.25 * max_ascent

        for x, word, font in self.line:
            y = baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font))

        self.cursor_x = HSTEP
        self.line = []
