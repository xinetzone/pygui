'''Some of the actions related to the graph.
'''
from tkinter import Canvas, StringVar, ttk


class CanvasMeta(Canvas):
    '''Graphic elements are composed of line(segment), rectangle, ellipse, and arc.
    '''

    def __init__(self, master=None, cnf={}, **kw):
        '''The base class of all graphics frames.

        :param master: a widget of tkinter or tkinter.ttk.
        '''
        super().__init__(master, cnf, **kw)

    def layout(self, row=0, column=0):
        '''Layout graphic elements with Grid'''
        # Layout canvas space
        self.grid(row=row, column=column, sticky='nwes')

    def draw_graph(self, graph_type, direction, color='blue', width=1, tags=None, **kwargs):
        '''Draw basic graphic elements.

        :param direction: Specifies the orientation of the graphic element. 
            Union[int, float] -> (x_0,y_0,x_,y_1), (x_0, y_0) refers to the starting point of 
            the reference brush (i.e., the left mouse button is pressed), and (x_1, y_1) refers to 
            the end position of the reference brush (i.e., release the left mouse button).
            Multipoint sequences are supported for 'line' and 'polygon',
             for example ((x_0, y_0), (x_1, y_1), (x_2, y_2)).
        :param graph_type: Types of graphic elements.
            (str) 'rectangle', 'oval', 'line', 'arc'(That is, segment), 'polygon'.
            Note that 'line' can no longer pass in the parameter 'fill', and 
            the remaining graph_type cannot pass in the parameter 'outline'.
        :param color: The color of the graphic element.
        :param width: The width of the graphic element.(That is, center fill)
        :param tags: The tags of the graphic element. 
            It cannot be a pure number (such as 1 or '1' or '1 2 3'), it can be a list, a tuple, 
            or a string separated by a space(is converted to String tupers separated by a blank space). 
            The collection or dictionary is converted to a string.
            Example:
                ['line', 'graph'], ('test', 'g'), 'line',
                ' line kind '(The blanks at both ends are automatically removed), and so on.
        :param style: Style of the arc in {'arc', 'chord', or 'pieslice'}.

        :return: Unique identifier solely for graphic elements.
        '''
        if tags is None:
            if graph_type in ('rectangle', 'oval', 'line', 'arc'):
                tags = f"{color} {graph_type}"
            else:
                tags = f'{color} graph'

        com_kw = {'width': width, 'tags': tags}
        kw = {**com_kw, 'outline': color}
        line_kw = {**com_kw, 'fill': color}
        if graph_type == 'line':
            kwargs.update(line_kw)
        else:
            kwargs.update(kw)
        func = eval(f"self.create_{graph_type}")
        graph_id = func(*direction, **kwargs)
        return graph_id


class GraphMeta(dict):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def __set__(self, instance, value):
        print('===> set', instance, value)
        self[instance] = value

    def __get__(self, instance, owner):
        return self[instance]


class SimpleGraph(CanvasMeta):
    color = GraphMeta()
    shape = GraphMeta()

    def __init__(self, master, shape, color, cnf={}, **kw):
        '''The base class of all graphics frames.

        :param master: a widget of tkinter or tkinter.ttk.
        '''
        super().__init__(master, cnf, **kw)
        self.color = color
        self.shape = shape

    def draw(self, direction, width=1, tags=None, **kw):
        return self.draw_graph(self.shape, direction, color=self.color, width=width, tags=tags, **kw)

    def add_row(self, direction, num, stride=10, width=1, tags=None, **kw):
        x0, y0, x1, y1 = direction
        stride = x1 - x0 + stride
        for k in range(num):
            direction = [x0+stride*k, y0, x1+stride*k, y1]
            self.draw(direction, width=width, tags=tags, **kw)

    def add_column(self, direction, num, stride=5, width=1, tags=None, **kw):
        x0, y0, x1, y1 = direction
        stride = y1 - y0 + stride
        for k in range(num):
            direction = [x0, y0+stride*k, x1, y1+stride*k]
            self.draw(direction, width=width, tags=tags, **kw)


class Drawing(CanvasMeta):
    '''Create graphic elements (graph) including rectangular boxes (which can be square points), 
        ovals (circular points), and segments.
        Press the left mouse button to start painting, release the left 
            mouse button for the end of the painting.
    Example
    ===============
    from tkinterx.graph.canvas_design import SelectorFrame
    from tkinterx.graph.canvas import Drawing
    from tkinter import Tk
    root = Tk()
    selector_frame = SelectorFrame(root, 'rectangle', 'yellow')
    self = Drawing(root, selector_frame, width=800, height=800, background='lightgray')
    self.layout(0, 0)
    selector_frame.layout(0, 1)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.mainloop()
    '''

    def __init__(self, master, selector_frame, after_time=160, cnf={}, **kw):
        '''Click the left mouse button to start painting, release
            the left mouse button to complete the painting.

        :param selector: The graphics selector, which is an instance of Selector.
        '''
        super().__init__(master, cnf, **kw)
        self.selector_frame = selector_frame
        self.after_time = after_time
        self.x = self.y = 0
        self.reset()
        self._draw_bind()

    def reset(self):
        self.first_x, self.first_y = 0, 0
        self.last_x, self.last_y = 0, 0
        self.on = False  # Used to record whether a painting is being made

    def update_xy(self, event):
        '''Press the left mouse button to record the coordinates of the left mouse button'''
        self.x = self.canvasx(event.x)
        self.y = self.canvasy(event.y)

    def update_bbox(self, event):
        x0, y0 = self.x, self.y  # The upper-left coordinates of the graph
        self.update_xy(event)
        x1, y1 = self.x, self.y  # Lower-right coordinates of the graph
        bbox = x0, y0, x1, y1
        return bbox

    def get_bbox(self, event):
        self.update_xy(event)
        return self.first_x, self.first_y, self.x, self.y

    def strat_draw(self, event):
        self.update_xy(event)
        self.first_x, self.first_y = self.x, self.y

    def mouse_draw(self, event):
        '''Release the left mouse button to finish painting.'''
        self.configure(cursor="arrow")
        self.after(self.after_time)
        bbox = self.get_bbox(event)
        self.create_graph(bbox)

    def mouse_move(self, event):
        self.on = True
        self.mouse_draw(event)

    def mouse_release(self, event):
        self.delete('temp')
        self.on = False
        self.mouse_draw(event)

    def create_graph(self, bbox):
        '''Create a graphic.

        :param bbox: (x0,y0,x1,y1)
        '''
        color, shape = self.selector_frame._selector.color, self.selector_frame._selector.shape
        x0, y0, x1, y1 = bbox
        cond1 = x0 == x1 and y0 == y1 and 'point' not in shape
        cond2 = 'point' in shape and (x0 != x1 or y0 != y1)
        if self.on:
            tags = (color, shape, 'temp')
        else:
            tags = (color, shape)
        kw = {
            'direction': bbox,
            'color': color,
            'tags': tags
        }
        if self.on:
            kw.update({"dash": 7})
        if cond1 or cond2:
            return
        else:
            return self.draw_graph(shape.split('_')[0], **kw)

    def tune_graph(self, event):
        '''Release the left mouse button to finish painting.'''
        self.configure(cursor="arrow")
        x0, y0, x1, y1 = self.get_bbox(event)
        current_graph_id = self.find_withtag('current')
        graph_id = current_graph_id if current_graph_id else self.find_closest(
            x0, y0)
        bbox = self.bbox(graph_id)
        self.coords(graph_id, *bbox[:2], x1, y1)

    def get_xy(self, event):
        self.configure(cursor="target")
        self.update_xy(event)

    def _draw_bind(self):
        self.bind("<1>", self.strat_draw)
        self.bind("<B1-Motion>",  self.mouse_move)
        self.bind("<ButtonRelease-1>", self.mouse_release)
        self.bind("<B3-Motion>", self.get_xy)
        self.bind("<3>", self.get_xy)
        self.bind("<ButtonRelease-3>", self.tune_graph)

    def layout(self, row=0, column=0):
        self.grid(row=row, column=column, sticky='nwes')


# class TrajectoryDrawing(Drawing):
#     '''Draw based on the mouse's trajectory.

#     Click the left mouse button to start painting, move the
#         left mouse button 'after_time' after the completion of painting.

#     Example
#     ===================
#     root = Tk()
#     selector = SelectorFrame(root)
#     meta = TrajectoryDrawing(root, selector, after_time=370, background='lightgray')
#     # Makes the master widget change as the canvas size
#     root.columnconfigure(0, weight=1)
#     root.rowconfigure(0, weight=1)
#     meta.layout(0, 0)
#     selector.layout(0, 1)
#     root.mainloop()
#     '''

#     def __init__(self, master,  selector, after_time=200, cnf={}, **kw):
#         super().__init__(master, selector, cnf, **kw)
#         self.after_time = after_time
#         self.bind("<1>", self.update_xy)
#         self.bind("<ButtonRelease-1>", self.update_xy)
#         self.bind("<Button1-Motion>", self.mouse_draw)

#     def mouse_draw(self, event):
#         '''Release the left mouse button to finish painting.'''
#         self.configure(cursor="arrow")
#         self.after(self.after_time)
#         bbox = self.get_bbox(event)
#         return self.create_graph(bbox)
