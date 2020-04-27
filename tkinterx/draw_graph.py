from tkinter import ttk, Tk
import json

from .graph.canvas_design import SelectorFrame
from .graph.canvas import Drawing, CanvasMeta


class DrawingWindow(Tk):
    def __init__(self, screenName=None, baseName=None, className='Tk', useTk=1, sync=0, use=None):
        super().__init__(screenName, baseName, className, useTk, sync, use)
        self.selector_frame = SelectorFrame(self, 'rectangle', 'yellow')
        self.drawing = Drawing(self, self.selector_frame,
                               width=800, height=800, background='lightgray')
        self.create_notebook()
        self.bunch = {}

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

    def save_graph(self, graph, path):
        with open(path, 'w') as fp:
            json.dump(graph, fp)

    def save_normal(self):
        all_graph = self.all_graph()
        self.save_graph(all_graph, path='normal.json')

    def load_graph(self, path):
        with open(path) as fp:
            bunch = json.load(fp)
        return bunch

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
        self.bunch = self.load_graph('normal.json')
        params = self.bunch2params(self.bunch)
        self.drawing.delete('all')
        for param in params.values():
            self.drawing.draw_graph(**param)

    def layout(self, row=0):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.drawing.layout(row=row, column=0)
        self.selector_frame.layout(row=row, column=1)
        self.notebook.grid(row=row+2, column=0)
        self.save_normal_button.grid(row=0, column=0, padx=2, pady=2)
        self.load_normal_button.grid(row=0, column=1, padx=2, pady=2)
        self.save_annotation_button.grid(row=0, column=0, padx=2, pady=2)
        self.load_annotation_button.grid(row=0, column=1, padx=2, pady=2)
        self.prev_annotation_button.grid(row=1, column=0, padx=2, pady=2)
        self.next_annotation_button.grid(row=1, column=1, padx=2, pady=2)

