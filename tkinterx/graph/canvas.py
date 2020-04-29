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

    def _create_regular_graph(self, graph_type, center, radius, color='blue', width=1, tags=None, **kw):
        '''Used to create a circle or square.
        :param graph_type: 'oval', 'rectangle'
        :param center: (x, y) The center of the regular_graph
        :param radius: Radius of the regular_graph
        '''
        x, y = center
        direction = [x-radius, y - radius, x+radius, y+radius]
        return self.draw_graph(graph_type, direction, color, width, tags, **kw)

    def create_circle(self, center, radius, color='blue', width=1, tags=None, **kw):
        '''
        :param center: (x, y) The center of the circle
        :param radius: Radius of the circle
        '''
        return self._create_regular_graph('oval', center, radius, color, width, tags, **kw)

    def create_square(self, center, radius, color='blue', width=1, tags=None, **kw):
        '''
        :param center: (x, y) The center of the square
        :param radius: Radius of the square
        '''
        return self._create_regular_graph('rectangle', center, radius, color, width, tags, **kw)

    def create_circle_point(self, location, color='blue', width=1, tags=None, **kw):
        '''
        :param location: (x, y) The location of the circle_point
        '''
        return self.create_circle(location, 0, color, width, tags, **kw)

    def create_square_point(self, location, color='blue', width=1, tags=None, **kw):
        '''
        :param location: (x, y) The location of the square_point
        '''
        return self.create_square(location, 0, color, width, tags, **kw)


class GraphMeta(CanvasMeta):
    '''Set some mouse event bindings to the keyboard.
    '''

    def __init__(self, master=None, cnf={}, **kw):
        '''The base class of all graphics frames.
        :param master: a widget of tkinter or tkinter.ttk.
        '''
        super().__init__(master, cnf, **kw)
        self._init_set()
        self.create_info_widgets()
        self._set_bind()

    def _init_set(self):
        self.xy_var = StringVar()
        self.x, self.y = 0, 0
        self.record_bbox = ['none']*4

    def create_info_widgets(self):
        self.info_frame = ttk.Frame(self.master)
        self.xy_label = ttk.Label(self.info_frame, textvariable=self.xy_var)

    def update_xy(self, event):
        self.x = self.canvasx(event.x)
        self.y = self.canvasy(event.y)
        self.record_bbox[2:] = self.x, self.y
        self.xy_var.set(f"Direction Vector: {self.record_bbox}")

    @property
    def closest_graph(self):
        xy = self.record_bbox[2:]
        if xy:
            return self.find_closest(*xy)

    def tune_graph(self, *args):
        '''Release the left mouse button to finish painting.'''
        self.configure(cursor="arrow")
        x1, y1 = self.record_bbox[2:]
        current_graph_id = self.find_withtag('current')
        graph_id = current_graph_id if current_graph_id else self.find_closest(
            x1, y1)
        bbox = self.bbox(graph_id)
        if 'none' not in bbox[:2]:
            self.coords(graph_id, *bbox[:2], x1, y1)

    def select_graph(self, *args):
        if self.closest_graph:
            self.itemconfigure(self.closest_graph, dash=10)

    def start_drawing(self, *args):
        self.record_bbox[:2] = self.x, self.y
        self.xy_var.set(f"Direction Vector: {self.record_bbox}")

    def mouse_draw_graph(self, graph_type, color='blue', width=1, tags=None, **kw):
        return self.draw_graph(graph_type, self.record_bbox, color, width, tags, **kw)

    def reset(self):
        self.record_bbox[:2] = ['none']*2

    def drawing(self,  graph_type='rectangle', color='blue', width=1, tags=None, **kw):
        self.delete('temp')
        if 'none' not in self.record_bbox:
            self.mouse_draw_graph(graph_type, color, width, tags, **kw)

    def finish_drawing(self, event=None, graph_type='rectangle', color='blue', width=1, tags=None, **kw):
        self.drawing(graph_type, color, width, tags, **kw)
        self.reset()

    def refresh_rectangle(self, event=None, graph_type='rectangle', color='purple', width=2, tags='temp', **kw):
        self.after(30, lambda: self.drawing(
            graph_type, color, width, tags, dash=5, **kw))

    def _set_bind(self):
        self.bind('<1>', self.start_drawing)
        self.master.bind('<Motion>', self.update_xy)
        self.bind('<Motion>', self.refresh_rectangle)
        self.bind('<ButtonRelease-1>', self.finish_drawing)
        self.bind('<Double-Button-1>', self.select_graph)
        self.bind('<ButtonRelease-3>', self.tune_graph)

    def layout(self, row=1, column=0):
        self.info_frame.grid(row=row, column=column)
        self.xy_label.grid(row=0, column=0)


class GraphCanvas(GraphMeta):
    '''Set some mouse event bindings to the keyboard.
    '''

    def __init__(self, master=None, cnf={}, **kw):
        '''The base class of all graphics frames.
        :param master: a widget of tkinter or tkinter.ttk.
        '''
        super().__init__(master, cnf, **kw)

    def refresh_rectangle(self, *args):
        self.after(30, lambda: self.draw_rectangle(
            tags='temp', dash=5, width=2))

    def draw_rectangle(self, min_size=(10, 10), color='blue', width=1, tags=None, *args, **kw):
        self.delete('temp')
        if 'none' not in self.record_bbox:
            self.mouse_draw_graph('rectangle', color, width, tags, **kw)

    def finish_drawing(self, *args, **kw):
        self.draw_rectangle(*args, **kw)
        self._init_set()
