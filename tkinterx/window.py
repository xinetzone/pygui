from tkinter import ttk, Tk, StringVar

from .graph.canvas_design import SelectorFrame
from .graph.canvas import Drawing, CanvasMeta
from .utils import save_bunch, load_bunch, mkdir


class DrawingWindow(Tk):
    def __init__(self, screenName=None, baseName=None, className='Tk', useTk=1, sync=0, use=None):
        super().__init__(screenName, baseName, className, useTk, sync, use)
        self.bunch = {}
        self._selected_tags = set()
        self.selector_frame = SelectorFrame(self, 'rectangle', 'blue')
        self.drawing = Drawing(self, self.selector_frame,
                               width=800, height=800, background='lightgray')
        self.create_notebook()
        self.tip_var = StringVar(self)
        self.tip_label = ttk.Label(self, textvariable=self.tip_var,
                            foreground='blue', background='yellow')
        self.tip_var.set("Start your creation!")
        self.bind('<1>', self.update_info)
        self.bind_move()

    @property
    def selected_tags(self):
        return self._selected_tags

    @selected_tags.setter
    def selected_tags(self, tags):
        if tags == 'current':
            self._selected_tags = self.find_withtag(tags)
        else:
            self._selected_tags = tags

    def select_graph(self, event, tags):
        self.configure(cursor="target")
        self.update_xy(event)
        self.selected_tags = tags

    def update_info(self, *args):
        xy = self.drawing.x, self.drawing.y
        self.tip_var.set(xy)

    def bind_move(self):
        self.bind('<Up>', lambda event: self.move_graph(event, 0, -1))
        self.bind('<Down>', lambda event: self.move_graph(event, 0, 1))
        self.bind('<Left>', lambda event: self.move_graph(event, -1, 0))
        self.bind('<Right>', lambda event: self.move_graph(event, 1, 0))
        self.bind('<F1>', self.clear_graph)
        self.bind('<Delete>', self.delete_graph)

    def find_closest(self):
        xy = self.drawing.x, self.drawing.y
        graph_id = self.drawing.find_closest(*xy)
        return graph_id

    def delete_graph(self, *args):
        graph_id = self.find_closest()
        self.drawing.delete(graph_id)

    def clear_graph(self, *args):
        self.drawing.delete('all')

    def move_graph(self, event, x, y):
        graph_id = self.find_closest()
        self.drawing.move(graph_id, x, y)
        
    def create_notebook(self):
        self.notebook = ttk.Notebook(
            self.selector_frame, width=200, height=200, padding=(5, 5, 5, 5))
        # first page, which would get widgets gridded into it
        self.normal = ttk.Frame(self.notebook, width=200,
                                height=200, padding=(5, 5, 5, 5))
        self.save_normal_button = ttk.Button(
            self.normal, text='Save', command=self.save_normal)
        self.load_normal_button = ttk.Button(
            self.normal, text='Load', command=self.load_normal)
        self.annotation = ttk.Frame(
            self.notebook, width=200, height=200, padding=(5, 5, 5, 5))
        self.save_annotation_button = ttk.Button(self.annotation, text='Save')
        self.load_annotation_button = ttk.Button(self.annotation, text='Load')
        self.next_annotation_button = ttk.Button(self.annotation, text='Next')
        self.prev_annotation_button = ttk.Button(self.annotation, text='Prev')
        self.notebook.add(self.normal, text='Normal')
        self.notebook.add(self.annotation, text='Annotation')

    def all_graph(self):
        cats = {}
        for graph_id in self.drawing.find_withtag('all'):
            tags = self.drawing.gettags(graph_id)
            bbox = self.drawing.bbox(graph_id)
            cats[graph_id] = {'tags': tags, 'bbox': bbox}
        return cats

    def save_normal(self):
        all_graph = self.all_graph()
        mkdir('data')
        save_bunch(all_graph, path='data/normal.json')

    def bunch2params(self, bunch):
        params = {}
        for graph_id, cats in bunch.items():
            tags = cats['tags']
            color, shape = tags
            graph_type = shape.split('_')[0]
            bbox = cats['bbox']
            params[graph_id] = {'tags': tags, 'color': color,
                                'graph_type': graph_type, 'direction': bbox}
        return params

    def load_normal(self):
        self.bunch = load_bunch('data/normal.json')
        params = self.bunch2params(self.bunch)
        self.clear_graph()
        for param in params.values():
            self.drawing.draw_graph(**param)

    def layout(self, row=0):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.tip_label.grid(row=row, columnspan=7)
        self.drawing.layout(row=row+1, column=0)
        self.selector_frame.layout(row=row+1, column=1)
        self.notebook.grid(row=row+3, column=0)
        self.save_normal_button.grid(row=0, column=0, padx=2, pady=2)
        self.load_normal_button.grid(row=0, column=1, padx=2, pady=2)
        self.save_annotation_button.grid(row=0, column=0, padx=2, pady=2)
        self.load_annotation_button.grid(row=0, column=1, padx=2, pady=2)
        self.prev_annotation_button.grid(row=1, column=0, padx=2, pady=2)
        self.next_annotation_button.grid(row=1, column=1, padx=2, pady=2)
