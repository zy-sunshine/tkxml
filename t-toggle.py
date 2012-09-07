from Tkinter import *
widget_value_map = {}
def connect_btn(widget, func, data):
    widget.bind("<ButtonRelease-1>", lambda event: func(data))
def enable_toggle(widget):
    print widget_value_map[widget].get() # this will get the widget's variable and get it value.
if __name__ == '__main__':
    window = Tk()
    v = IntVar()
    ck_btn = Checkbutton(window, variable=v)
    widget_value_map[ck_btn] = v
    connect_btn(ck_btn, enable_toggle, ck_btn)
    ck_btn.pack()
    window.mainloop()
