



#from auth_check import auth_ping
from textual.message import Message
from textual.app import App, ComposeResult
from textual.screen import Screen, ModalScreen
from textual.widgets import Static, Button, Input
from textual.containers import Container, VerticalScroll, Horizontal, Grid
import os
from textual import events, on, work
from .scan_v2 import Scan_serials
from .confmscn import Confirm_Screen
from .DFTable import DataFrameTable

from .textual_file_selector import Selector_Widget_Screen
#from pax_pickle import get_term_ids_v2
#from better_file_picker import pax_session
from .functionsScreen import FunctionsScreen
from .SingleTermDetailsScreen import TerminalDetailsScreen
from .SingleTermDetailsScreen import parseList
from .commands import reboot
from .operations import apiPaxFunctions, PushConfigs, resetTerminals
from .notasync import findSingleTerminal, buildSingleRequest 





"""async def single_disable_delete(serial):
   auth_ping()
   t_df = get_term_ids_v2([serial])
   await disable_terminals(t_df)
   await a_delete_terms(t_df)


async def single_activate(serial):
   auth_ping()
   t_df = get_term_ids_v2([serial])
   await activate_terminals(t_df)


async def single_get_details(serial):
   auth_ping()
   t_df = get_term_ids_v2([serial])
   await a_get_extra_dict(t_df)"""
  




def scan_pax_groups():
    path = "pax_groups"
    path_list = os.listdir(path)
    filtered_list = [folder for folder in path_list if not folder.startswith(".")]
    filtered_list.sort()
    path_list.sort()
    fake_file=["_","Terminal_Groups_live","no_groups_:(","to_get_started_:)"]
    fakelist=["_","This_is_where","You_currently_have", "Click_ADD_NEW_GROUP"]
    name_list = []
    holder = []
    return_list = []
    for folder in filtered_list:
        new_path = os.path.join(path,folder)
        with os.scandir(new_path) as it:           
            for entry in it:
                if not entry.name.startswith('.'):  
                    a_tuple = (folder,entry.name.removesuffix(".pkl"))
                    name_list.append(entry.name.removesuffix(".pkl"))
    if not name_list:
        for x,y in list(zip(fakelist,fake_file)):
            tup = (x,y)
            holder.append(tup)
            holder = return_list 
    else: return_list = list(zip(filtered_list,name_list))
    
    return return_list


class New_Group_Screen(ModalScreen[bool]):


    CSS_PATH = "css_lib/scan_or_import_screen.tcss"


    def compose(self) -> ComposeResult:
        yield Grid(
            Static("Please Select Input Method:", id="question"),
            Button("1. Scan or Key-In", id="scan", variant="primary"),
            Button("2. Import from SpreadSheet", id="import", variant="primary"),
            id="confirmscreen")
  
    @on(Button.Pressed)
    def scan_screen(self, event: Button.Pressed):
        if event.button.id == 'scan':
            self.app.push_screen(Scan_serials())
        elif event.button.id == 'import':
            self.app.push_screen(Selector_Widget_Screen())




class Main_Menu_Sceen(Screen):

    CSS_PATH = "css_lib/combining_layouts.tcss"


    def __init__(self):
      
        self.term_lookup_list = [
           {'name':'Activate', 'id':'activate', 'variant':'success', 'classes':'buttons'}, #'function':single_activate},
           {'name':'Delete','id':'delete','variant':'error','classes':'buttons'},# 'function':single_disable_delete},
           {'name':'View Details','id':'term_details','variant':'warning','classes':'buttons'},#'funtion':single_get_details}
       ]


        self.fun_dict = {
           "new":{"c_screen":Confirm_Screen, "d_screen":FunctionsScreen},
           "activate":{"c_screen":Confirm_Screen, "d_screen":""},
           "term_details":{"c_screen": Confirm_Screen, "d_screen": TerminalDetailsScreen}
       }
        super().__init__()
  
    def compose(self) -> ComposeResult:
        with Container(id="app-grid"):
            with VerticalScroll(id="left-pane"):
                yield Static("Terminal Groups", classes="titleheader")
                self.group_list = scan_pax_groups()
                self.id_list = []
                for self.group in self.group_list:
                    self.id_list.append(str(self.group[0]))
                    yield Button(f"{self.group[0]}\n{self.group[1]}",name=str(self.group[1]),id=str(self.group[0]))
                if len(self.group_list) < 7:
                    yield Button("ADD NEW", id="new", variant="success")
            with VerticalScroll(id="top-center"):
                yield Static("Terminal Lookup", classes="titleheader")
                yield Input(placeholder="S/N")
                for button in self.term_lookup_list:
                   yield Button(button['name'], id=button['id'], variant=button['variant'], classes=button['classes']) # type: ignore
            with VerticalScroll(id="bottom-left"):
                yield(Static("Help", classes="titleheader"))
            with VerticalScroll(id="bottom-middle"):
                yield(Static("Quick Functions - Scan & Go", classes="titleheader"))
                yield Button("Activate Terminals", id="quickactivate", classes="gtask-buttons")
                yield Button("Get Terminal Details", id = "details", classes="gtask-buttons")
                yield Button("Dectivate Terminals", id="deactivate",classes="gtask-buttons")
                yield Button("Move Terminals", id="move", classes="gtask-buttons")
                yield Button("Delete Terminals", id ="quickdelete", classes="gtask-buttons")
                yield Button("Placeholder", id="foop", classes="gtask-buttons")
          
    @on(Button.Pressed)
    @work
    async def do_stuff(self, event: Button.Pressed) ->None:
        self.notify(str(event.button.name))
        
        """if event.button.id in set(self.id_list):
            if await self.app.push_screen_wait(Confirm_Screen(f"Open this group {event.button.name}?")):
                self.app.push_screen(GroupFuctionsScreen(str(os.path.join('Iface_Pax_Groups',event.button.id,f'{event.button.name}.pkl')))) # type: ignore
        elif event.button.id == 'new':
            if await self.app.push_screen_wait(Confirm_Screen("Create New Terminal Group?")):
                await self.app.push_screen_wait(New_Group_Screen())"""
        
        user_input = self.query_one(Input)
        
        for k,v in self.fun_dict.items():
            if event.button.id == k in self.fun_dict:
            
                if self.app.push_screen(Confirm_Screen("Do the thing?")): # type: ignore
                    self.app.push_screen(dict(v)["d_screen"](user_input.value)) #type: ignore
            else:pass
        #elif event.button.id == ""




      
class Main_Menu_App(App):
  
   def on_mount(self) -> None:
       self.push_screen(Main_Menu_Sceen())




if __name__ == "__main__":
   app = Main_Menu_App()
   app.run()
