from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from typing import List, Tuple
import logging

class FileSelectorNotebookFrame(ttk.Notebook):
    """Notebook containing differnet file types selection

    Args:
        ttk (_type_): _description_
    """
    
    def __init__(self,parent: ttk.Frame):
        """Create notebook object containing tabs for selecting different files

        Args:
            parent (ttk.Frame): _description_
        """
        super().__init__(parent)

        self.file_types = {
            "Session": FileType("Session Files",["*.xml"]),
            "Geometry": FileType("Geometry Files",["*.nekg"]),
            "Output": FileType("Output Files",["*.fld"]),
            "Checkpoint": FileType("Checkpoint Files",["*.chk"]),
            "Filter": FileType("Filter Files", ["*.fce"]),
            "Supporting": FileType("Supporting Files", ["*.pdf",".jpg","*.jpeg","*.png"])
        }

        self.session_frame = FileSelectorFrame(self,self.file_types["Session"])
        self.add(self.session_frame,text="Session")

        self.geometry_frame = FileSelectorFrame(self,self.file_types["Geometry"])
        self.add(self.geometry_frame,text="Geometry")

        self.output_frame = FileSelectorFrame(self,self.file_types["Output"])
        self.add(self.output_frame,text="Output")

        self.checkpoint_frame = FileSelectorFrame(self,self.file_types["Checkpoint"])
        self.add(self.checkpoint_frame,text="Checkpoint")
        
        self.filter_frame = FileSelectorFrame(self,self.file_types["Filter"])
        self.add(self.filter_frame,text="Filter")

        self.supporting_frame = FileSelectorFrame(self,self.file_types["Supporting"])
        self.add(self.supporting_frame, text="Supporting")
        
    @property
    def session_file_list(self) -> List[str]:
        return self.session_frame.file_list

    @property
    def geometry_file_list(self) -> List[str]:
        return self.geometry_frame.file_list
    
    @property
    def output_file_list(self) -> List[str]:
        return self.output_frame.file_list

    @property
    def checkpoint_file_list(self) -> List[str]:
        return self.checkpoint_frame.file_list

    @property
    def filter_file_list(self) -> List[str]:
        return self.filter_frame.file_list
    
    @property
    def supporting_file_list(self) -> List[str]:
        return self.supporting_frame.file_list

    def get_file_list(self) -> List[str]:
        return self.session_file_list + self.geometry_file_list + self.output_file_list + \
                self.checkpoint_file_list + self.filter_file_list + self.supporting_file_list

class FileSelectorFrame(ttk.Frame):
    """Frame for selecting files

    Args:
        ttk (_type_): _description_
    """
    def __init__(self,parent: ttk.Frame,file_type: 'FileType'):
        """_summary_

        Args:
            parent (ttk.Frame): _description_
            file_type (FileType): _description_
        """
        super().__init__(parent)
        self.file_type = file_type

        self.grid_rowconfigure(0, weight=1)  # Row with Listbox expands
        self.grid_columnconfigure(2, weight=1)  # Column with Listbox expands
        
        buttons = self._create_buttons()
        buttons.grid(column=0,row=0,sticky=(E,W))

        #set up list box with scroller for displaying files
        self.file_listbox: Listbox = Listbox(self,selectmode=EXTENDED)
        scrollbar: Scrollbar = Scrollbar(self,command=self.file_listbox.yview)
        scrollbar_horizontal: Scrollbar = Scrollbar(self,command=self.file_listbox.xview,orient=HORIZONTAL) #help view full path 
        self.file_listbox.config(yscrollcommand=scrollbar.set,xscrollcommand=scrollbar_horizontal.set)
        scrollbar.config(command=self.file_listbox.yview)
        scrollbar_horizontal.config(command=self.file_listbox.xview)
        self.file_listbox.grid(row=0,column=2,sticky=(N,S,E,W))
        scrollbar.grid(row=0,column=3,sticky=(N,S))
        scrollbar_horizontal.grid(row=1,column=2,sticky=(W,E))

    def _create_buttons(self) -> ttk.Frame:
        """Button used with listbox to add and delete files

        Returns:
            ttk.Frame: _description_
        """
        frame = ttk.Frame(self)
        frame.grid_columnconfigure(0,uniform="group1")

        # button to add files
        find_files_button = ttk.Button(frame,text="Add Files",command=self._select_files_listbox)
        find_files_button.grid(column=0,row=0,sticky=(E,W))

        # button to remove files
        delete_file_button = ttk.Button(frame,text="Delete Files",command=self._delete_files_listbox)
        delete_file_button.grid(column=0,row=1,sticky=(E,W))

        return frame

    def _select_files_listbox(self) -> None:
        """Add files selected from filedialogue into listbox, ensuring no duplication
        """
        filetype = self.file_type.get_filetype()
        selected_files = filedialog.askopenfilenames(title="Select Files", filetypes=(filetype,))

        if selected_files:
            existing_files = set(self.file_list)  # Use a set for efficient lookup

            for file in selected_files:
                if file not in existing_files:  # Check for duplicates
                    self.file_listbox.insert(END, file)
                    existing_files.add(file)  # Keep the set updated
                else:
                    print(f"Duplicate file: {file} - not added.")

            print(f"Files: {self.file_list}")  # Print updated file list
        else:
            print("No Files Selected")

    def _delete_files_listbox(self) -> None:
        """Delete selected files in the listbox
        """
        selection_indices = self.file_listbox.curselection()

        if selection_indices:
            # 1. Get the items to delete *before* modifying the listbox
            items_to_delete = [self.file_listbox.get(index) for index in selection_indices]

            # 2. Delete from the listbox (reverse order to prevent issues with shifting indices)
            for index,item in zip(sorted(selection_indices, reverse=True),sorted(items_to_delete,reverse=True)):
                self.file_listbox.delete(index)

            print(f"Deleted files. Remaining: {self.file_list}")

    @property
    def file_list(self) -> List[str]:
        return [self.file_listbox.get(i) for i in range(self.file_listbox.size())]

class FileType:
    """Describes what acceptable file extensions should be present in file dialogue
    """
    def __init__(self,name: str,extensions: List[str]):
        self.name = name
        self.extensions = extensions

    def get_filetype(self) -> Tuple[str, Tuple[str, ...]]:
        """Return the acceptable file extension in a format acceptable for filedialog filetypes=() argument

        Returns:
            Tuple[str, Tuple[str, ...]]: _description_
        """
        return (self.name,tuple(self.extensions))