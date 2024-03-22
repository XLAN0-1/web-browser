import sys
sys.path.insert(1, "/home/xlan/web_browser/uri")
sys.path.insert(2, "/home/xlan/web_browser/cache")

import sockets_cache
import browser_cache
import http_uri

import tkinter
WIDTH, HEIGHT = 1500, 1000
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100


class Browser:
    def __init__(self):
        self.scroll = 0
        self.cache = sockets_cache.SocketsCache()
        self.window = tkinter.Tk()
        self.width = WIDTH
        self.height = HEIGHT
        self.canvas = tkinter.Canvas(
            self.window,
            width = WIDTH,
            height = HEIGHT
        )
        self.canvas.pack(fill="both", expand=1)

        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<MouseWheel>", self.mousescroll)
        self.window.bind("<Configure>", self.resize)

    def scrolldown(self, e):
        if self.height + self.scroll  < self.display_list[-1][1]:
            self.scroll += SCROLL_STEP
            self.draw()

    def scrollup(self, e):
        if self.scroll > 0:
            self.scroll -= SCROLL_STEP
            self.draw()
    
    def mousescroll(self, e):
        print("ya")
        print(e.delta)

    def resize(self, e):
        # Only resize when the window changes in interval of 50
        if (abs(self.width - e.width) > 50 or abs(self.height - e.height) > 50):
            self.width = e.width
            self.height = e.height

            self.display_list = self.layout(self.url_text)
            self.draw()
        
    def layout(self, text):
        cursor_x, cursor_y = HSTEP, VSTEP
        display_list = []

        for c in text:
            display_list.append((cursor_x, cursor_y, c))
            cursor_x += HSTEP

            if cursor_x + 15>= self.width - HSTEP:
                cursor_y += VSTEP
                cursor_x = HSTEP
        
        self.document_height = cursor_y
        return display_list
    
    def draw_scrollbar(self, max):
        if (self.document_height > self.height):
            lower = ((max - self.height) / self.document_height) * self.height
            higher = (max / self.document_height) * self.height

            self.canvas.create_rectangle(self.width - 15, lower, self.width, higher, fill="blue")
        
    def draw(self):
        self.canvas.delete("all")
        max = 0
        for x, y, c in self.display_list:
            if y > self.scroll + self.height: continue
            if y + VSTEP < self.scroll: continue

            if y > max:
                max = y
            self.canvas.create_text(x, y - self.scroll, text=c)
        self.draw_scrollbar(max)


    def show_blank_page(self):
        self.display_list = self.layout("")
        self.draw()

    def load(self, uri):
        try:
            url = http_uri.HttpURI(url=uri, cache=self.cache)
            text = url.lex(url.make_request())
            self.url_text = text
            self.display_list = self.layout(text)
            self.draw()
        except:
            self.show_blank_page()
