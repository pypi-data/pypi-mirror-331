import tkinter as tk
import tkinter.ttk as ttk
from tkinter import scrolledtext

import logging

class TerminalHandler(logging.Handler):
    """Custom logging handler

    Args:
        logging (_type_): _description_
    """
    def __init__(self, terminal: 'TerminalWidget'):
        super().__init__()
        self.terminal = terminal

    def emit(self, record):
        """Writes a log to the terminal

        Args:
            record (_type_): _description_
        """
        msg = self.format(record)
        level = record.levelname  # Get the log level

        tag = None  # Default tag
        if level == "ERROR":  # Check for ERROR level
            tag = "error"  # Use the "error" tag

        self.terminal.write(msg + "\n", tag=tag)  # Pass the tag to write()
        self.terminal.terminal.update_idletasks()

class TerminalWidget(ttk.Frame):
    """Terminal widget to emulate a terminal

    Args:
        ttk (_type_): _description_
    """
    def __init__(self, parent: ttk.Frame, height=10, **kwargs):
        """Creates a widget containing a text terminal

        Args:
            parent (ttk.Frame): Parent frame
            height (int, optional): Height of terminal. Defaults to 10.
        """
        super().__init__(parent, **kwargs)

        self.terminal = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, state=tk.DISABLED, height=height
        )
        self.terminal.pack(fill=tk.BOTH, expand=True)

        # Configure the "error" tag for red text
        self.terminal.tag_configure("error", foreground="red")  # Set foreground to red

    def write(self, text: str, tag=None):
        """Appends text to the terminal.

        Args:
            text: The text to add.
            tag: An optional tag to apply to the text (for styling).
        """
        self.terminal.config(state=tk.NORMAL)
        self.terminal.insert(tk.END, text, tag)  # Use the tag here
        self.terminal.see(tk.END)
        self.terminal.config(state=tk.DISABLED)

    def clear(self):
        """Clears the terminal content."""
        self.terminal.config(state=tk.NORMAL)
        self.terminal.delete(1.0, tk.END)  # Delete from beginning to end
        self.terminal.config(state=tk.DISABLED)

    def tag_configure(self, tag, **kwargs):
        """Configures a tag for styling text."""
        self.terminal.tag_configure(tag, **kwargs)