from tkinter import *
from tkinter import ttk

class HeaderFrame(ttk.Frame):
    def __init__(self,parent: ttk.Frame):
        super().__init__(parent)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        style: ttk.Style = ttk.Style()
        style.configure("Header.TLabel", font=("Helvetica", 24, "bold"), underline=True)

        header: ttk.Label = ttk.Label(self, text="Welcome to NekUpload", style="Header.TLabel")
        header.grid(column=0, row=0, columnspan=2, sticky=N)

        description_text: str = "This is an interactive GUI upload and validation pipeline for Nektar++ datasets. " + \
            "Please complete the setup instructions found in the User Guide before proceeding [link]."
        description: ttk.Label = ttk.Label(self, text=description_text, wraplength=600)
        description.grid(column=0, row=1, columnspan=2, sticky=N)