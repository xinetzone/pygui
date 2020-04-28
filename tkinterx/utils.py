from pathlib import Path
import json
from tkinter import ttk


def save_bunch(bunch, path):
    with open(path, 'w') as fp:
        json.dump(bunch, fp)


def load_bunch(path):
    with open(path) as fp:
        bunch = json.load(fp)
    return bunch


def mkdir(root_dir):
    '''依据给定名称创建目录'''
    path = Path(root_dir)
    if not path.exists():
        path.mkdir()


class Frame(ttk.LabelFrame):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.save_button = ttk.Button(self, text='Save')
        self.load_button = ttk.Button(self, text='Load')
        self.layout(row=0)
        
    def layout(self, row=0):
        self.load_button.grid(row=row, column=0)
        self.save_button.grid(row=row, column=1)
