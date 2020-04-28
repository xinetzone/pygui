from tkinter import ttk, Tk, StringVar, filedialog
from PIL import Image, ImageTk
from pathlib import Path

from .graph.canvas_design import SelectorFrame
from .graph.canvas import Drawing, CanvasMeta
from .utils import save_bunch, load_bunch, mkdir, Frame
from .image_utils import ImageLoader


class DrawingWindow(Tk):
    def __init__(self, screenName=None, baseName=None, className='Tk', useTk=1, sync=0, use=None):
        super().__init__(screenName, baseName, className, useTk, sync, use)
        self.reset()
        self.selector_frame = SelectorFrame(self, 'rectangle', 'blue')
        self.drawing = Drawing(self, self.selector_frame,
                               width=800, height=600, background='lightgray')
        self.create_notebook()
        self.tip_var = StringVar(self)
        self.tip_label = ttk.Label(self, textvariable=self.tip_var,
                            foreground='blue', background='yellow')
        self.tip_var.set("Start your creation!")
        self.bind('<Motion>', self.update_info)
        self.bind_move()

    def reset(self):
        self.bunch = {}
        self.image_names = ()
        self._image_loader = None

    def update_info(self, *args):
        if not self.drawing.on:
            self.drawing.update_xy(*args)
        xy = self.drawing.x, self.drawing.y
        self.tip_var.set(xy)

    def bind_move(self):
        self.bind('<Up>', lambda event: self.move_graph(event, 0, -1))
        self.bind('<Down>', lambda event: self.move_graph(event, 0, 1))
        self.bind('<Left>', lambda event: self.move_graph(event, -1, 0))
        self.bind('<Right>', lambda event: self.move_graph(event, 1, 0))
        self.bind('<F1>', self.clear_graph)
        self.bind('<F2>', self.fill_normal)
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
            self.normal, text='Save', command=lambda : self.save_graph('all'))
        self.load_normal_button = ttk.Button(
            self.normal, text='Load', command=self.load_normal)
        self.annotation = ttk.Frame(
            self.notebook, width=200, height=200, padding=(5, 5, 5, 5))
        self.image_frame = Frame(self.annotation, text='images', padding=(5, 5, 5, 5))
        self.next_image_button = ttk.Button(self.image_frame, text='Next')
        self.prev_image_button = ttk.Button(self.image_frame, text='Prev')
        self.annotation_frame = Frame(self.annotation, text='annotations', padding=(5, 5, 5, 5))
        self.notebook.add(self.annotation, text='Annotation')
        self.notebook.add(self.normal, text='Normal')
        self.init_command()
    
    def init_command(self):
        self.image_frame.load_button['command'] = self.load_images
        self.next_image_button['command'] = self.next_image
        self.prev_image_button['command'] = self.prev_image
        self.annotation_frame.save_button['command'] = lambda: self.save_graph('rectangle')
        self.annotation_frame.load_button['command'] = self.load_graph

    def next_image(self):
        self.drawing.delete('image')
        self.image_loader.current_id += 1
        self.image_loader.create_image(self.drawing, 0, 0, anchor='nw')

    def prev_image(self):
        self.drawing.delete('image')
        self.image_loader.current_id -= 1
        self.image_loader.create_image(self.drawing, 0, 0, anchor='nw')

    def get_graph(self, tags):
        cats = {}
        for graph_id in self.drawing.find_withtag(tags):
            tags = self.drawing.gettags(graph_id)
            bbox = self.drawing.bbox(graph_id)
            cats[graph_id] = {'tags': tags, 'bbox': bbox}
        return cats

    def set_path(self, tags):
        if tags == 'all':
            return 'data/normal.json'
        else:
            return 'data/annotations.json'

    def save_graph(self, tags):
        graph = self.get_graph(tags)
        mkdir('data')
        path = self.set_path(tags)
        current_image_path = self.image_loader.current_path
        if current_image_path:
            self.bunch.update({self.image_loader.current_name: graph})
            print(self.bunch)
            save_bunch(self.bunch, path)
        else:
            save_bunch(graph, path)

    def load_graph(self):
        self.bunch = load_bunch('data/annotations.json')
        root = self.bunch['root']
        self.image_loader = ImageLoader(root)
        self.image_names = [f"{root}/{image_name}" for image_name in self.bunch if image_name!= root]
        self.image_loader.current_id = 0
        self.create_image(root)
        self.draw_graph(self.bunch[self.image_loader.current_name])

    def draw_graph(self, cats):
        params = self.bunch2params(cats)
        self.clear_graph()
        for param in params.values():
            self.drawing.draw_graph(**param)

    @property
    def image_loader(self):
        return self._image_loader

    @image_loader.setter
    def image_loader(self, new):
        self._image_loader = new

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
        self.draw_graph(self.bunch)

    def fill_normal(self, *args):
        graph_id = self.find_closest()
        color = self.drawing.selector_frame._selector.color
        self.drawing.itemconfigure(graph_id, fill=color)

    def create_image(self, root):
        self.image_loader = ImageLoader(root)
        self.image_loader.create_image(self.drawing, 0, 0, anchor='nw')
    
    def load_images(self, *args):
        #self.image_names = filedialog.askopenfilenames(filetypes=[("All files", "*.*"), ("Save files", "*.png")])
        root =  filedialog.askdirectory()
        self.bunch['root'] = root
        self.create_image(root)
        
    def layout(self, row=0):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.drawing.layout(row=row, column=0)
        self.selector_frame.layout(row=row, column=1)
        self.tip_label.grid(row=row+1, sticky='we')
        self.notebook.grid(row=row+2, column=0)
        self.save_normal_button.grid(row=0, column=0, padx=2, pady=2)
        self.load_normal_button.grid(row=0, column=1, padx=2, pady=2)
        self.image_frame.grid(row=0, column=0, padx=2, pady=2)
        self.prev_image_button.grid(row=1, column=0, padx=2, pady=2)
        self.next_image_button.grid(row=1, column=1, padx=2, pady=2)
        self.annotation_frame.grid(row=1, column=0, padx=2, pady=2)
        
