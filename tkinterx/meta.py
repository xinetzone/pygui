from tkinter import Toplevel, ttk, Tk
from tkinter import filedialog, StringVar, messagebox


class Bunch(dict):
    def __init__(self, master, *args, **kw):
        '''依据 key 绑定 tkinter 的组件的 textvariable
        '''
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
        self.ok_button = ttk.Button(self, text='确认', command=self.run)
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


class Root(Tk):
    def __init__(self):
        super().__init__()
        style = ttk.Style()
        style.configure("C.TButton",
                        foreground="green",
                        background="white",
                        relief='raise',
                        justify='center',
                        font=('YaHei', '15', 'bold'))
        self.meta_button = ttk.Button(self, text='meta',
                                      command=self.ask_meta,
                                      style="C.TButton")

    def ask(self, window_type):
        window = window_type(self)
        window.transient(self)
        self.wait_window(window)

    def ask_meta(self):
        self.ask(WindowMeta)

    def layout(self):
        self.meta_button.place(x=20, y=20)
