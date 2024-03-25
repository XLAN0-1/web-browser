import sys
sys.path.append("..")

import tkinter.font
import tkinter
from layout import Layout
from uris.http_uri import HttpURI, Text, Tag
from cache import sockets_cache, browser_cache




WIDTH, HEIGHT = 1500, 1000
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100


class Browser:
    def __init__(self):
        self.scroll = 0
        self.document_height = 0
        self.cache = sockets_cache.SocketsCache()
        self.window = tkinter.Tk()
        self.width = WIDTH
        self.height = HEIGHT
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT
        )
        self.canvas.pack(fill="both", expand=1)

        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<MouseWheel>", self.mousescroll)
        self.window.bind("<Configure>", self.resize)

    def scrolldown(self, e):
        if self.height + self.scroll < self.display_list[-1][1]:
            self.scroll += SCROLL_STEP
            self.draw()

    def scrollup(self, e):
        if self.scroll > 0:
            self.scroll -= SCROLL_STEP
            self.draw()

    def mousescroll(self, e):
        if e.delta < 0:
            self.scrolldown(e)
        else:
            self.scrollup(e)

    def resize(self, e):
        pass
        # Only resize when the window changes in interval of 50
        # if (abs(self.width - e.width) > 50 or abs(self.height - e.height) > 50):
        #     self.width = e.width
        #     self.height = e.height

        #     self.layout.get_display_list(e.width, e.height)
        #     self.display_list = self.layout.display_list


        #     self.draw()

    def draw_scrollbar(self, max):
        if (self.document_height > self.height):
            lower = ((max - self.height) / self.document_height) * self.height
            higher = (max / self.document_height) * self.height

            self.canvas.create_rectangle(
                self.width - 15, lower, self.width, higher, fill="blue")

    def draw(self):
        self.canvas.delete("all")
        max = 0
        for x, y, c, f in self.display_list:
            if y > self.scroll + self.height:
                continue
            if y + VSTEP < self.scroll:
                continue

            if y > max:
                max = y
            self.canvas.create_text(
                x, y - self.scroll, text=c, font=f, anchor="nw")
            
        self.draw_scrollbar(max)

    def show_blank_page(self):
        print("BLANK PAGE")
        self.display_list = self.layout("")
        self.draw()

    def load(self, uri):
        try:
            url = HttpURI(url=uri, cache=self.cache)
            text = url.make_request()  #"<small>a</small><big>A</big>"  
            tokens = url.lex(text)
            self.layout = Layout(tokens)
            self.display_list = self.layout.display_list
            self.document_height = self.display_list[-1][1]
            print("load")
            print(len(self.display_list))
            self.draw()
        except Exception as e:
            print(e)
            self.show_blank_page()

