from tkinter import ttk, StringVar
import json

from .canvas import SimpleGraph


class SelectorMeta(SimpleGraph):
    '''A selection icon that sets the shape and color of the graphic.

    Example:
    ======================
    from tkinter import Tk
    root = Tk()
    select = SelectorMeta(root)
    select.grid()
    root.mainloop()
    '''
    colors = 'red', 'blue', 'black', 'purple', 'green', 'skyblue', 'yellow', 'white', 'orange', 'pink'
    shapes = 'rectangle', 'oval', 'line', 'oval_point', 'rectangle_point'

    def __init__(self, master, shape, color, cnf={}, **kw):
        '''The base class of all graphics frames.

        :param master: a widget of tkinter or tkinter.ttk.
        '''
        super().__init__(master, shape, color, cnf, **kw)
        self.start, self.end = 15, 50
        self.create_color()
        self.create_shape()

    def create_color(self):
        '''Set the color selector'''
        self.create_text((self.start, self.start),
                         text='color', font='Times 15', anchor='w')
        x0, y0, x1, y1 = self.start+10, self.start-10, self.end, self.end-20
        for k, color in enumerate(SelectorMeta.colors):
            tags = f"color {color}"
            t = 7+30*(k+1)
            direction = x0+t, y0, x1+t, y1
            self.draw(direction, width=2, tags=tags, fill=color)

    def create_shape(self):
        '''Set the shape selector'''
        self.create_text((self.start, self.start+27),
                         text='shape', font='Times 15', anchor='w')
        x0, y0, x1, y1 = self.start+18, self.start+20, self.end+8, self.end+10
        for k, shape in enumerate(SelectorMeta.shapes):
            t = 30*(k+1)
            direction = x0+t, y0, x1+t, y1
            fill = 'blue' if 'point' in shape else 'white'
            width = 10 if shape == 'line' else 1
            kw = {
                'width': width,
                'fill': fill,
                'tags': f"shape {shape}"
            }
            self.draw_graph(shape.split('_')[0], direction, 'blue', **kw)


class Selector(SelectorMeta):
    def __init__(self, master, shape, color, cnf={}, **kw):
        '''Events that bind colors and shapes
        '''
        super().__init__(master, shape, color, cnf, **kw)
        self.bind_selector()
        self.info_var = StringVar()
        self.update_info()

    def bind_selector(self):
        [self.color_bind(self, color)
         for color in SelectorMeta.colors]
        [self.shape_bind(self, shape)
         for shape in SelectorMeta.shapes]

    def update_info(self, *args):
        '''Update info information.'''
        text = f"{self.color} {self.shape}"
        self.info_var.set(text)

    def update_color(self, new_color):
        self.color = new_color
        self.update_info()

    def update_shape(self, new_shape):
        '''Update graph_type information.'''
        self.shape = new_shape
        text = f"You Selected: {self.color},{self.shape}"
        self.update_info()

    def color_bind(self, canvas, color):
        canvas.tag_bind(color, '<1>', lambda e: self.update_color(color))

    def shape_bind(self, canvas, shape):
        canvas.tag_bind(shape, '<1>',
                        lambda e: self.update_shape(shape))


class SelectorFrame(ttk.Frame):
    '''Binding the left mouse button function of the graphics selector to achieve the color and
        shape of the graphics change.

    Example:
    ===============================================
    from tkinter import Tk
    root = Tk()
    self = SelectorFrame(root, 'rectangle', 'yellow')
    self.layout()
    root.mainloop()
    '''

    def __init__(self, master=None, shape='rectangle', color='blue', **kw):
        '''The base class of all graphics frames.

        :param master: a widget of tkinter or tkinter.ttk.
        :param graph_type: The initial shape value of the graph.
        :param color: The initial color value of the graph.
        '''
        super().__init__(master, **kw)
        self._selector = Selector(
            self, shape, color, background='lightgreen', width=360, height=80)
        self.create_info()
        self._selector.info_var.trace_add('write', self.update_select)

    def create_info(self):
        self.info_var = StringVar()
        self.update_select()
        self.info_entry = ttk.Entry(self, textvariable=self.info_var, width=36)
        self.info_entry['state'] = 'readonly'

    def update_select(self, *args):
        self.info_var.set(self._selector.info_var.get())

    def save_label(self):
        info = f"{self._selector.color} {self._selector.shape}"
        with open('cat.json', 'w') as fp:
            json.dump(info, fp)

    def layout(self, row=0, column=1):
        '''The layout's internal widget.'''
        self._selector.grid(row=0, column=0, sticky='we')
        self.info_entry.grid(row=1, column=0)
        self.grid(row=row, column=column, sticky='nwes')
