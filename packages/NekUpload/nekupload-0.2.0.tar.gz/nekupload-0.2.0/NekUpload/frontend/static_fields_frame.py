from tkinter import * 
import tkinter.ttk as ttk
from datetime import date
from . import style_guide

class StaticFieldsFrame(ttk.LabelFrame):
    def __init__(self,parent: ttk.Frame):
        super().__init__(parent, text="Basic Info")
        """Create a frame with basic information to be filled out. Static as no funky things going on with the widget formatting.
        """
        
        self._is_read_user_guide: StringVar = StringVar()
        self._api_key_env_var: StringVar = StringVar()
        self._host_name: StringVar = StringVar()
        self._community_slug: StringVar = StringVar()
        self._title: StringVar = StringVar()
        self._publication_date: StringVar = StringVar()

        #tick box to serve as reminder for user to set host name environment variable
        read_user_info_check: ttk.Checkbutton = ttk.Checkbutton(self,text="Have you read User Guide for setting up environment variables?",
                                       command=None,variable=self._is_read_user_guide,
                                       onvalue="True",offvalue="False")
        read_user_info_check.grid(row=2,column=0,sticky=W,padx=5,pady=.5)

        #ask user for what the environment variables are for the api key
        api_key_env_label = ttk.Label(self,text="Environment Variable for API Key: ")
        api_key_env_label.grid(row=3,column=0,sticky=W,padx=5,pady=.5)
        self.api_key_entry = ttk.Entry(self,textvariable=self._api_key_env_var)
        self.api_key_entry.grid(row=3,column=1,sticky=E,padx=5,pady=.5)

        #for highlighting missing fields and turning off red when user is inputting
        self.api_key_entry.bind("<FocusOut>",lambda event: style_guide.highlight_mandatory_entry_on_focus_out(self.api_key_entry))
        self.api_key_entry.bind("<FocusIn>",lambda event: style_guide.highlight_mandatory_entry_on_focus_in(self.api_key_entry))

        #ask user for host name
        host_label = ttk.Label(self,text="Host Name URL: ")
        host_label.grid(row=4,column=0,sticky=W,padx=5,pady=.5)
        self.host_name_entry = ttk.Entry(self,textvariable=self._host_name)
        self.host_name_entry.grid(row=4,column=1,sticky=E,padx=5,pady=.5)

        #for highlighting missing fields and turning off red when user is inputting
        self.host_name_entry.bind("<FocusOut>",lambda event: style_guide.highlight_mandatory_entry_on_focus_out(self.host_name_entry))
        self.host_name_entry.bind("<FocusIn>",lambda event: style_guide.highlight_mandatory_entry_on_focus_in(self.host_name_entry))

        #ask user for community url slug
        community_label = ttk.Label(self,text="Community (URL slug or UUID): ")
        community_label.grid(row=5,column=0,sticky=W,padx=5,pady=.5)
        self.community_entry = ttk.Entry(self,textvariable=self._community_slug)
        self.community_entry.grid(row=5,column=1,sticky=E,padx=5,pady=.5)

        #for highlighting missing fields and turning off red when user is inputting
        self.community_entry.bind("<FocusOut>",lambda event: style_guide.highlight_mandatory_entry_on_focus_out(self.community_entry))
        self.community_entry.bind("<FocusIn>",lambda event: style_guide.highlight_mandatory_entry_on_focus_in(self.community_entry))
   
        #ask for title of the dataset
        title_label: ttk.Label = ttk.Label(self, text="Title: ")
        title_label.grid(row=6, column=0, sticky=W, padx=5, pady=.5)
        self.title_widget: ttk.Entry = ttk.Entry(self, textvariable=self._title) 
        self.title_widget.grid(row=6, column=1, sticky=E, padx=5, pady=.5)

        #for highlighting missing fields and turning off red when user is inputting
        self.title_widget.bind("<FocusOut>",lambda event: style_guide.highlight_mandatory_entry_on_focus_out(self.title_widget))
        self.title_widget.bind("<FocusIn>",lambda event: style_guide.highlight_mandatory_entry_on_focus_in(self.title_widget))

        #ask for publication date, pre-populate with current date
        publication_date_label: ttk.Label = ttk.Label(self, text="Publication Date: ") 
        publication_date_label.grid(row=7, column=0, sticky=W, padx=5, pady=.5)
        self._publication_date.set(self._get_current_iso8601_date())  
        self.publication_date_widget: ttk.Entry = ttk.Entry(self, textvariable=self._publication_date) 
        self.publication_date_widget.grid(row=7, column=1, sticky=E, padx=5, pady=.5)

        #for highlighting missing fields and turning off red when user is inputting
        self.publication_date_widget.bind("<FocusOut>",lambda event: style_guide.highlight_mandatory_entry_on_focus_out(self.publication_date_widget))
        self.publication_date_widget.bind("<FocusIn>",lambda event: style_guide.highlight_mandatory_entry_on_focus_in(self.publication_date_widget))

        #presets
        preset_label = ttk.Label(self,text="Setting: ")
        preset_label.grid(row=0, column=0, sticky=W, padx=5, pady=.5)

        self.setting = StringVar()
        options = ["AE Database","InvenioRDM Demo","Custom"]
        setting_combobox = ttk.Combobox(self,textvariable=self.setting,values=options,state="readonly")
        setting_combobox.current(0)
        self.set_AE_db_default() #ensure correct starting state
        setting_combobox.grid(row=0,column=1)
        
        setting_combobox.bind("<<ComboboxSelected>>",self.on_combobox_select)

    def on_combobox_select(self,event: Event):
        """Callback for combobox selection, sets default values in some fields

        Args:
            event (Event): _description_
        """
        selected_value = event.widget.get()

        if selected_value == "AE Database":
            self.set_AE_db_default()
        elif selected_value == "InvenioRDM Demo":
            self.set_demo_default()
        else:
            self.set_default()

    #Sets settings for default config
    def set_AE_db_default(self):
        """Set default settings for sending to AE database
        """
        self._host_name.set("https://data.ae.ic.ac.uk")
        self._community_slug.set("nektar") #don't actually know yet

    def set_default(self):
        """No default settings
        """
        self._host_name.set("")
        self._community_slug.set("")

    def set_demo_default(self):
        """Set default settings for sending to a demo instance
        """
        self._host_name.set("https://inveniordm.web.cern.ch")
        self._community_slug.set("test_nekupload")

    @property
    def is_read_user_guide(self):
        return self._is_read_user_guide.get()

    @is_read_user_guide.setter
    def is_read_user_guide(self, value: str):
        self._is_read_user_guide.set(value)

    @property
    def api_key_env_var(self):
        return self._api_key_env_var.get()

    @api_key_env_var.setter
    def api_key_env_var(self, value: str):
        self._api_key_env_var.set(value)

    @property
    def host_name(self):
        return self._host_name.get()

    @host_name.setter
    def host_name(self, value: str):
        self._host_name.set(value)

    @property
    def community_slug(self):
        return self._community_slug.get()

    @community_slug.setter
    def community_slug(self, value: str):
        self._community_slug.set(value)

    @property
    def title(self):
        return self._title.get()

    @title.setter
    def title(self, value: str):
        self._title.set(value)

    @property
    def publication_date(self):
        return self._publication_date.get()

    @publication_date.setter
    def publication_date(self, value: str):
        self._publication_date.set(value)

    def _get_current_iso8601_date(self) -> str:
        today: date = date.today() 
        return today.isoformat()

    def get_title_entry_widget(self) -> ttk.Entry:
        return self.title_widget

    def get_api_key_entry_widget(self) -> ttk.Entry:
        return self.api_key_entry

    def get_host_name_entry_widget(self) -> ttk.Entry:
        return self.host_name_entry

    def get_community_entry_widget(self) -> ttk.Entry:
        return self.community_entry

    def get_publication_date_entry_widget(self) -> ttk.Entry:
        return self.publication_date_widget