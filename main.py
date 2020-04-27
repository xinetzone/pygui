from tkinter import ttk
from tkinterx.draw_graph import DrawingWindow


if __name__ == "__main__":
    root = DrawingWindow()
    hello_label = ttk.Label(root, text="Start your creation!",
                            foreground='blue', background='yellow')
    hello_label.grid(row=0, columnspan=7)
    root.layout(1)
    root.mainloop()