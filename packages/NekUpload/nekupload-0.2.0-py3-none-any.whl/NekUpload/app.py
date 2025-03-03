from tkinter import *
from tkinter import ttk #holds the more modern widgets

from typing import List
from NekUpload.metadataModule import *
from NekUpload.uploadModule import invenioRDM
from NekUpload.validator import NektarValidator
import os
from dotenv import load_dotenv

from NekUpload.frontend.terminal_widget import TerminalWidget,TerminalHandler
from NekUpload.frontend.header_frame import HeaderFrame
from NekUpload.frontend.static_fields_frame import StaticFieldsFrame
from NekUpload.frontend.dynamic_fields_frame import DynamicFieldsFrame
from NekUpload.frontend.file_selector import FileSelectorNotebookFrame
from NekUpload.frontend import style_guide
import logging

class NekUploadGUI:
    def __init__(self,root: Tk) -> None:
        self.root: Tk = root
        self.mainframe: ttk.Frame = self._create_mainframe()
        
        self.header_frame = HeaderFrame(self.mainframe)
        self.header_frame.grid(column=0,row=0,columnspan=2,sticky=(N,W,E,S))

        self.static_fields_frame = StaticFieldsFrame(self.mainframe)
        self.static_fields_frame.grid(column=0,row=2,sticky=(N,E,W,S))

        self.dynamic_fields_frame = DynamicFieldsFrame(self.root,self.mainframe)
        self.dynamic_fields_frame.grid(column=1, row=2, rowspan=3, sticky=(N,S))

        style = ttk.Style()
        style.configure("Subheader.TLabel", font=("TkDefaultFont", 14, "bold"))
        self.upload_descriptor_label = ttk.Label(self.mainframe,text="Upload Files Here",style="Subheader.TLabel")
        self.upload_descriptor_label.grid(row=3,column=0,sticky=(E,W))

        self.file_selector_notebook_frame = FileSelectorNotebookFrame(self.mainframe)
        self.file_selector_notebook_frame.grid(row=4,column=0,sticky=(E,W))

        self.terminal = TerminalWidget(root)
        self.terminal.grid(row=6,column=0,columnspan=5,sticky=(E,W))

        #configure terminal for logging        
        logger = logging.getLogger()  # Get the root logger
        logger.setLevel(logging.INFO)
        terminal_handler = TerminalHandler(self.terminal)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') #format of message
        terminal_handler.setFormatter(formatter)
        logger.addHandler(terminal_handler)

        self.submit_button: ttk.Button = ttk.Button(self.mainframe, text="Submit", command=self.submit_form)
        self.submit_button.grid(row=7, column=1, sticky=E)

    def _create_mainframe(self) -> ttk.Frame:
        mainframe = ttk.Frame(self.root)
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)
        return mainframe
    
    def _check_mandatory_static_fields(self) -> bool:
        is_mandatory_fields_missing = False

        if not self.static_fields_frame.get_title_entry_widget().get():
            style_guide.show_error_in_entry(self.static_fields_frame.get_title_entry_widget())
            is_mandatory_fields_missing = True

        if not self.static_fields_frame.get_api_key_entry_widget().get():
            style_guide.show_error_in_entry(self.static_fields_frame.get_api_key_entry_widget())
            is_mandatory_fields_missing = True

        if not self.static_fields_frame.get_community_entry_widget().get():
            style_guide.show_error_in_entry(self.static_fields_frame.get_community_entry_widget())
            is_mandatory_fields_missing = True

        if not self.static_fields_frame.get_host_name_entry_widget().get():
            style_guide.show_error_in_entry(self.static_fields_frame.get_host_name_entry_widget())
            is_mandatory_fields_missing = True

        if not self.static_fields_frame.get_publication_date_entry_widget().get():
            style_guide.show_error_in_entry(self.static_fields_frame.get_publication_date_entry_widget())
            is_mandatory_fields_missing = True

        return is_mandatory_fields_missing

    def submit_form(self) -> None: 
        #check all fields filled
        if self._check_mandatory_static_fields():
            logging.error("Mandatory Fields Missing")
            return
        
        is_read_user_guide = self.static_fields_frame.is_read_user_guide
        if not is_read_user_guide or is_read_user_guide == "False":
            logging.error("User guide not read. Please read user guide and check box after.")
            return    
        
        authors_from_app: List[InvenioOrgInfo | InvenioPersonInfo] = self.dynamic_fields_frame.author_list
        if not authors_from_app:
            logging.error("No authors specified. At least one required")
            return

        #check files
        session_file_list = self.file_selector_notebook_frame.session_file_list
        if not session_file_list:
            logging.error("No session files specified. One is required")
            return
        
        if len(session_file_list) > 1:
            logging.error(f"{len(session_file_list)} session files selected. Only one should be specified")
            return 
        
        geometry_file_list = self.file_selector_notebook_frame.geometry_file_list        
        if not geometry_file_list:
            logging.error("No geometry files specified. One is required")
            return
        
        if len(geometry_file_list) > 1:
            logging.error(f"{len(geometry_file_list)} geometry files selected. Only one should be specified")

        output_files_list = self.file_selector_notebook_frame.output_file_list
        if not output_files_list:
            logging.error("No output files specified. One is required")
            return
        
        if len(output_files_list) > 1:
            logging.error(f"{len(output_files_list)} output files selected. Only one should be specified")
            return

        chk_file_list = self.file_selector_notebook_frame.checkpoint_file_list
        other_files_list = self.file_selector_notebook_frame.filter_file_list + \
                            self.file_selector_notebook_frame.supporting_file_list

        validator = NektarValidator(session_file_list[0],geometry_file_list[0],output_files_list[0],
                                    chk_file_list,other_files_list)

        try: 
            validator.validate()
        except Exception as e:
            logging.error(e)
            return

        title: str = self.static_fields_frame.title
        publication_date: str = self.static_fields_frame.publication_date
        
        #ASSIGN USERS
        author_list: List[InvenioOrgInfo | InvenioPersonInfo] = []
        for author in authors_from_app:
            author_info: InvenioOrgInfo | InvenioPersonInfo = None
            
            if author["type"] == "personal":
                given_name = author["given_name"]
                last_name = author["last_name"]
                author_info = InvenioPersonInfo(given_name,last_name)
            elif author["type"] == "organizational":
                name = author["name"]
                author_info = InvenioOrgInfo(name)

            if author["id"] != "":
                mapping = {"ORCID" : IdentifierType.ORCID}
                id = Identifier(author["id"],mapping[author["id_type"]])
                author_info.add_identifier(id)
                
            #also affiliations, but not supported in backend for now
            author_list.append(author_info)

        #create metadata
        metadata = InvenioMetadata(title,publication_date,author_list,"dataset")
        metadata.add_publisher("NekUpload App")
        metadata.add_description("This was uploaded via NekUpload app")
        metadata_payload = metadata.get_metadata_payload()
        metadata_json = {"metadata": metadata_payload}
        print(metadata_json)

        upload_manager = invenioRDM()
        
        URL = self.static_fields_frame.host_name
        COMMUNITY_SLUG = self.static_fields_frame.community_slug
        API_KEY_ENV_VAR = self.static_fields_frame.api_key_env_var
        file_list = self.file_selector_notebook_frame.get_file_list()
        load_dotenv()

        if file_list:
            upload_manager.upload_files(URL,os.getenv(API_KEY_ENV_VAR,None),file_list,metadata_json,COMMUNITY_SLUG)
        else:
            print("Failed to upload as no files detected")

def main() -> None:
    root: Tk = Tk() 
    app: NekUploadGUI = NekUploadGUI(root)
    root.title("NekUpload")
    root.mainloop()

if __name__ == "__main__":
    main()