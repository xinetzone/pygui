from tkinter import Toplevel, ttk, Tk
from tkinter import filedialog, StringVar, messagebox


def askokcancel(window, title='Do You need to exit?', message=None):
    if messagebox.askokcancel(title, message):
        window.destroy()
    else:
        window.deiconify()


def showwarning(window, title='Warning', message='Please check your input'):
    if messagebox.showwarning(title, message):
        window.deiconify()


def ask_window(tk_root, window_type):
    '''Pass information through a window
    :param tk_root: An instance of a Tk or an instance of its subclass
    :param window_type: WindowMeta or its subclasses
    '''
    window = window_type(tk_root)
    window.transient(tk_root)
    tk_root.wait_window(window)
    return window.bunch


class Bunch(dict):
    def __init__(self, master, *args, **kw):
        super().__init__(*args, **kw)
        self.__dict__ = self
        self.master = master

    def set_key(self, key):
        self[key] = StringVar(self.master)

    def set_ttk_text(self, widget, key):
        '''
        :param widget: 'ttk.Combobox', 'ttk.Label',  'ttk.Entry',
            'ttk.Menubutton', 'ttk.Spinbox', 'ttk.Button'
        '''
        self.set_key(key)
        widget['textvariable'] = self[key]


class WindowMeta(Toplevel):
    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        self.bunch = Bunch(self)
        self.widgets = []
        self.ok_button = ttk.Button(self, text='OK', command=self.run)
        self.layout()

    def add_row(self, text, key):
        label = ttk.Label(self, text=text)
        self.bunch.set_key(key)
        if 'path' in key or 'dir' in key:
            label.bind('<1>', lambda event: self.get_name(event, key))
        entry = ttk.Entry(self, width=20, textvariable=self.bunch[key])
        self.widgets.append([label, entry])

    def get_name(self, event, key):
        if 'path' in key:
            name = filedialog.askopenfilename()
        elif 'dir' in key:
            name = filedialog.askdirectory()
        self.bunch[key].set(name)
        return name

    def layout(self):
        self.create_widget()
        for m, row in enumerate(self.widgets):
            for n, widget in enumerate(row):
                widget.grid(row=m, column=n, sticky='we')
        self.ok_button.grid(sticky='we')

    def run(self):
        NotImplemented

    def create_widget(self):
        NotImplemented
