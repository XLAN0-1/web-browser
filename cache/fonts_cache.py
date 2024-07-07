import tkinter.font
import tkinter

class FontsCache:
    def __init__(self):
        self.FONTS = {}

    def get_font(self, size, weight, slant):
        key = (size, weight, slant)

        if key not in self.FONTS:
            font = tkinter.font.Font(size=size, weight=weight, slant=slant)
            label = tkinter.Label(font=font)
            self.FONTS[key] = (font, label)

        return self.FONTS[key][0]