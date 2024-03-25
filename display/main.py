import browser
import tkinter

if __name__ == "__main__":
    import sys
    browser.Browser().load(sys.argv[1])
    tkinter.mainloop()

    # b = browser.Browser()
    # b.dummy()
    # tkinter.mainloop()
    