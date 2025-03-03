from tkinter import * 
import tkinter.ttk as ttk
from typing import Dict,Any,List
from .create_author_window import CreateAuthorPersonWindow,CreateAuthorOrgWindow

class DynamicFieldsFrame(ttk.LabelFrame):
    def __init__(self,root: Tk, parent: ttk.Frame):
        super().__init__(parent, text="Author(s)")

        #root window
        self.root = root

        #authors
        self.authors: List[Dict[str,Any]] = []

        #allow addition of author as a person
        create_author_person_button: ttk.Button = ttk.Button(self,text="Add Person",command=self._create_author_person)
        create_author_person_button.grid(row=0,column=0,sticky=W)

        #allow additiong of author as an organisation
        create_author_org_button: ttk.Button = ttk.Button(self,text="Add Org",command=self._create_author_org)
        create_author_org_button.grid(row=0,column=1,sticky=W)

        #have a listbox to specify the creation
        self.author_listbox: Listbox = Listbox(self,selectmode=EXTENDED)
        scrollbar_y: Scrollbar = Scrollbar(self,command=self.author_listbox.yview)
        scrollbar_x: Scrollbar = Scrollbar(self,command=self.author_listbox.xview,orient=HORIZONTAL)
        self.author_listbox.config(yscrollcommand=scrollbar_y.set,xscrollcommand=scrollbar_x)
        scrollbar_y.config(command=self.author_listbox.yview)
        scrollbar_x.config(command=self.author_listbox.xview)

        self.author_listbox.grid(row=1,column=0,columnspan=2,sticky=(N,S))
        scrollbar_x.grid(row=2,column=0,columnspan=2,sticky=(W,E))
        scrollbar_y.grid(row=1,column=2,sticky=(N,S))

        #add a delete button
        delete_button = ttk.Button(self,text="Delete",command=self._delete_selected_author)
        delete_button.grid(row=3,column=1)

    def _create_author_person(self) -> None:
        """Opens a new window with a form to specify the author as a person
        """
        
        # The lambda function will be executed later when triggered by an event.
        # By that time, new_window will have already been created by __init__.
        # This works because lambdas capture variables by reference, not by value.
        new_window = CreateAuthorPersonWindow(self.root,lambda: self.submit_author_person_info(new_window))

    def _create_author_org(self) -> None:
        """Opens a new window with a form to specify the author as an organisation
        """
        # The lambda function will be executed later when triggered by an event.
        # By that time, new_window will have already been created by __init__.
        # This works because lambdas capture variables by reference, not by value.
        new_window = CreateAuthorOrgWindow(self.root,lambda: self.submit_author_org_info(new_window))

    def submit_author_person_info(self,window: CreateAuthorPersonWindow):
        """Takes person data from CreateAuthorPersonWindow and stores it. Closes window on success.

        Args:
            window (CreateAuthorPersonWindow): Window containing form to specify user info
        """
        author_data = {}
        author_data['type'] = 'personal'
        author_data['given_name'] = window.given_name
        author_data['last_name'] = window.last_name
        author_data['name'] = f"{author_data['given_name']} {author_data['last_name']}"
        author_data['affiliation'] = window.affiliation
        author_data['id_type'] = window.id_type
        author_data['id'] = window.id

        print("Author Data: ", author_data)

        self.authors.append(author_data)
        self.author_listbox.insert(END,f"{author_data['name']}")
        
        window.destroy()

    def submit_author_org_info(self,window: CreateAuthorOrgWindow):
        """Takes person data from CreateAuthorOrgWindow and stores it. Closes window on success.

        Args:
            window (CreateAuthorOrgWindow): Window containing form to specify organisation info
        """
        author_data = {}
        author_data['type'] = 'organizational'
        author_data['name'] = window.name
        author_data['affiliation'] = window.affiliation
        author_data['id_type'] = window.id_type
        author_data['id'] = window.id

        print("Author Data: ", author_data)

        self.authors.append(author_data)
        self.author_listbox.insert(END,f"{author_data['name']}")
        
        window.destroy()

    def _delete_selected_author(self) -> None:
        """Delete the selected author from the list of authors. Deletion is accomplished via a Button connected to a Listbox.
        """
        selection_indices = self.author_listbox.curselection()
        if selection_indices:
            # 1. Get the items to delete *before* modifying the listbox
            items_to_delete = [self.author_listbox.get(index) for index in selection_indices]

            # 2. Delete from the listbox (reverse order to prevent issues with shifting indices)
            for index,item in zip(sorted(selection_indices, reverse=True),sorted(items_to_delete,reverse=True)):
                self.author_listbox.delete(index)

                #delete from self.authors using the index
                # self.authors should mirror same order as listbox
                try:
                    self.authors.pop(index)
                except ValueError:
                    print(f"Warning: Item '{item}' not found in self.authors")  # Handle potential mismatch

        print(self.authors)

    @property
    def author_list(self) -> List[Dict[str,Any]]:
        """Read only access to list of authors

        Returns:
            List[Dict[str,Any]]: Dictionary containing information on authors
        """
        return self.authors