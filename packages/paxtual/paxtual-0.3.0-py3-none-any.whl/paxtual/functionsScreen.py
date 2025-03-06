import datetime
import os
import socket
import logging
import pandas as pd
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Header, Footer
from textual import on, work
from textual.containers import Container, VerticalScroll
from .DFTable import DataFrameTable
from .ti_labels_iccid import create_pdf
from .confmscn import Confirm_Screen
from .SingleTermDetailsScreen import parseList
from .SingleTermDetailsScreen import TerminalDetailsScreen
from .commands import reboot
from .operations import apiPaxFunctions, PushConfigs, resetTerminals, closeGroup
#from .submit_to_sheets import add_production_data, format_dataframe

def drop_specified_columns(df, drop_list):
    """
    Checks a pandas DataFrame for columns in the provided list and drops them.

    Args:
        df (pandas.DataFrame): The DataFrame to process.
        drop_list (list): A list of column names to drop.

    Returns:
        pandas.DataFrame: The DataFrame with the specified columns dropped.
    """

    columns_to_drop = [col for col in drop_list if col in df.columns]

    if columns_to_drop:
        df = df.drop(columns=columns_to_drop)
        print(f"Dropped columns: {columns_to_drop}")  # Optional: Print dropped columns
    else:
        print("No columns from the drop list found in the DataFrame.") #Optional: print if no columns were dropped.

    return df

def get_workstation_id():
    hostname = socket.gethostname()
    workstationMap = {'L-5CG0035QJ4': 'Eval2', 'L-5CG012F4P7': 'Config3', 'L-5CG9437NPP': 'Config2', 'L-5CG9258BPB': 'Config1'}
    try:
        return workstationMap.get(hostname)
    except KeyError:
        workStationId = "unidentfiedWS"
        return workStationId

class FunctionsScreen(Screen):
    """
    A screen to display and perform functions on a group of Pax terminals.
    """

    BINDINGS = [("escape", "app.pop_screen", "BACK")]
    CSS_PATH = "css_lib/group_gunctions.tcss"

    def __init__(self, df: pd.DataFrame, logger: logging) -> None:
        """
        Initializes the FunctionsScreen with a DataFrame of terminal information.

        Args:
            df (pd.DataFrame): A DataFrame containing terminal details.
            logger: Logging instance
        """

        self.df = df
        self.logger = logger
        self.button_list = [
            {'name': 'Reset Group', 'id': 'reset', 'classes': 'gtask-buttons'},
            {'name': 'Activate Group', 'id': 'activate', 'classes': 'gtask-buttons'},
            {'name': 'Deactivate', 'id': 'deactivate', 'classes': 'gtask-buttons'},
            {'name': 'Reboot Group', 'id': 'reboot', 'classes': 'gtask-buttons'},
            {'name': 'Refresh Terminal Detials', 'id': 'details', 'classes': 'gtask-buttons'},
            {'name': 'Create Ticket Labels', 'id': 'labels', 'classes': 'gtask-buttons'},
            {'name': 'Close Group', 'id': 'close', 'classes': 'gtask-buttons'},
        ]
        
        self.op = apiPaxFunctions()  # Create an instance of apiPaxFunctions
        self.configop = PushConfigs()  # Create an instance of PushConfigs
        self.operations = {
            "activate": self.op.activateTerminals,
            "details": self.op.startPaxGroup,
            "deactivate": self.op.disableTerminals,
            "reboot": reboot, 
            "reset": resetTerminals,
            "labels": create_pdf,
            "payanywhere": self.configop.paPushByReseller,
            "broadpos": self.configop.pushBroadPosEPX,
            "other": self.configop.pushBroadPos_nonEPX
        }

        self.functionDict = {}
        #self.accessory_serials = self.df[['serialNo', 'accessory']].set_index('serialNo')['accessory'].to_dict()

        super().__init__()
        self.logger.debug("FunctionsScreen initialized") #log initialization
        if os.path.isdir("Groups"):
            pass
        else: os.mkdir("Groups")
        self.current_date = str(datetime.datetime.today().strftime('%m.%d.%Y.%H.%M'))
        self.wsid = get_workstation_id()
        self.filename = f"{self.wsid}_pax_group_log_{self.current_date}.pkl"
        self.filepath = os.path.join("Groups", self.filename)
        self.df.to_pickle(self.filepath)
        
    def compose(self) -> ComposeResult:
        """
        Composes the screen with widgets to display the terminal data and buttons for actions.
        """

        yield Header(name='PaxTools')
        with Container(id="app-grid"):
            with VerticalScroll(id="top-pane"):
                yield DataFrameTable()  # Display the terminal data in a table
            with VerticalScroll(id="bottom-left"):
                yield Static("Available Tasks", classes="titleheader")
                for button in self.button_list:
                    yield Button(button['name'], id=button['id'], classes=button['classes'])
            with VerticalScroll(id="bottom-right"):
                yield Static("Configuration Tasks", classes="titleheader")
                yield Button("Config for PayAnywhere", id="payanywhere", classes="buttons")
                yield Button("Config for BroadPOS - EPX", id="broadpos", classes="buttons")
                yield Button("Config for BroadPOS - Not EPX", id="other", classes="buttons")
        yield Footer()

    async def on_mount(self):
        """
        Called when the screen is mounted. Adds the DataFrame to the table and reorders columns.
        """

        self.table = self.query_one(DataFrameTable)
        # Define the desired column order
        self.new_order = ['serialNo', 'status', 'modelName', 'pn', 'resellerName', 'iccid', 'accessory', 'id']
        # Reorder columns based on the new order, keeping only those present in the new order list
        self.reordered_columns = [col for col in self.new_order if col in self.df.columns]  
        self.ordered_df = self.df[self.reordered_columns]
        self.table.add_df(self.ordered_df)  # Add the DataFrame to the table

    @on(Button.Pressed)
    @work
    async def do_stuff(self, event: Button.Pressed):
        """
        Handles button press events to perform actions on the group of terminals.
        """
        
        if event.button.id in self.operations.keys():
            operation = self.operations.get(event.button.id)
            self.logger.info(f"User has selected {event.button.id}")
            # Display a confirmation screen before proceeding with the operation
            if await self.app.push_screen_wait(Confirm_Screen("Please confirm terminal network connection and open PaxStore client on device.")):  
                try:
                    pickled_df = pd.read_pickle(self.filepath)
                    persistent_values = pickled_df[['serialNo', 'accessory', 'pn']].set_index('serialNo').to_dict('index')

                    result = await operation(idList=self.df['id'], serialNoList=self.df['serialNo'], df=self.df)
                    self.notify(str(result))
                    self.logger.info(f"Operation {event.button.id} complete")
                    refresh = await self.op.startPaxGroup(self.df['serialNo'])
                    self.ndf = pd.DataFrame(refresh).drop_duplicates(subset=["serialNo"])
                    refresh_reordered_columns = [col for col in self.new_order if col in self.ndf.columns]
                    self.reorg = self.ndf[refresh_reordered_columns]
                    # Restore accessory serials before updating the table
                    self.restore_persistent_values(persistent_values, self.reorg)
                    self.table.update_df(self.reorg)
                    self.df = self.reorg
                except Exception as e:
                    self.logger.exception(f"Exception encountered: {e}")
                    # If an error occurs, display an error message
                    if await self.app.push_screen_wait(Confirm_Screen(f"Encountered Error. Stop messing up")):  
                        pass
        elif event.button.id == "close":
            if await self.app.push_screen_wait(Confirm_Screen("Close current terminal Group?")):
                self.logger.info("User has seleceted Close Group")
                short_date = str(datetime.datetime.today().strftime('%m.%d.%Y'))
                new_path = f"Groups/{self.wsid}_Completed_{short_date}"
                if os.path.isdir(new_path):
                    pass
                else: os.mkdir(new_path)
                drop = ["id","tid","merchantName", "imei", "screenResolution", "language", "ip", "macAddress", "cellId"]
                filteredDataFrame = self.df.drop(self.df[(self.df.modelName=="Q20L")|(self.df.modelName=="Q10A")].index) # Filter out specific models
                fn = f"{self.wsid}_paxLog_{short_date}.xlsx"
                full_path = os.path.join(new_path,fn)
                #filteredDataFrame.drop(columns=drop)
                #add_production_data(format_dataframe(filteredDataFrame))
                f2 = drop_specified_columns(filteredDataFrame,drop)

                try:
                    # Try to load the existing workbook
                    workbook = openpyxl.load_workbook(full_path)
                    sheet = workbook.active  # Get the active (single) sheet
                    max_row = sheet.max_row + 1  # Start appending from the next row
                    for r in dataframe_to_rows(f2.astype(str), header=False, index=False):
                        sheet.append(r)
                    workbook.save(full_path)
                except FileNotFoundError:
                    with pd.ExcelWriter(full_path, engine='openpyxl') as writer:
                        f2.astype(str).to_excel(writer, sheet_name='Sheet1', index=False, )
                self.logger.info(f"Terminal log updated {full_path}")
                #add_production_data
                close = await closeGroup(self.df)
                self.logger.info("Terminals moved to Production")
                if await self.app.push_screen_wait(Confirm_Screen(f"Group Log successfully created {full_path} Press ok to quit:")):
                    self.logger.info("Group completed")
                    self.app.exit()
    
    def restore_persistent_values(self, persistent_values, refreshed_df):
        """Restores persistent values in the refreshed DataFrame."""
        for serial, values in persistent_values.items():
            if serial in refreshed_df['serialNo'].values:
                for col, value in values.items():
                    if pd.isna(refreshed_df.loc[refreshed_df['serialNo'] == serial, col].values[0]):
                        refreshed_df.loc[refreshed_df['serialNo'] == serial, col] = value
    @work
    @on(DataFrameTable.CellSelected)
    async def note_cell(self, event: DataFrameTable.CellSelected):
        """
        Handles cell selection events in the DataFrameTable.

        If a serial number is selected, displays a confirmation screen to view the terminal details.
        """

        if event.value in self.df['serialNo'].values: #if the clicked cell's value matches an item in the list of serial numbers
            # Display a confirmation screen before navigating to the terminal details screen
            if await self.app.push_screen_wait(Confirm_Screen(message=f"View {event.value} Terminal Page?")):  
                self.logger.info(f"User selected to view {event.value} terminal details")
                try:
                    dList = [event.value] #clicked terminal serial number in a list
                    termDetails = await parseList(dList)  # Get terminal details and application data
                    self.app.notify(str(termDetails))
                    # Navigate to the TerminalDetailsScreen to display the information
                    self.app.push_screen(TerminalDetailsScreen(termDetails))  
                except Exception as e:
                    self.logger.exception(f"Exception encountered: {e}")
                    # If an error occurs, display an error message with instructions
                    if await self.app.push_screen_wait(Confirm_Screen(f"An error occured! Make sure the terminal is connected to a network and the PaxStore client is open on the Device!")):  
                        pass    


