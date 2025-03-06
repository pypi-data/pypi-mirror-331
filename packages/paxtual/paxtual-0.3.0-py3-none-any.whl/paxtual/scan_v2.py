
import logging
import datetime
from textual.app import App, ComposeResult
from textual.widgets import Static, Input, Header,Footer
from textual.screen import ModalScreen
from .confmscn import Confirm_Screen
from textual import on, work
import pandas as pd
from .operations import apiPaxFunctions
from .serialNoValidator import SerialNoValidator
from .paxStoreChecker import PaxStoreChecker, NA_Handler
from .functionsScreen import FunctionsScreen
from .replace_terminal_screen import ReplaceTerminal
from .list_stringifyer import stringify_list


CURRENT_DATE = str(datetime.datetime.today().strftime('%m.%d.%Y.%H.%M'))
LOG_FILE = f"pax_terminal_app{CURRENT_DATE}.log" 
LOG_LEVEL = logging.DEBUG 

logging.basicConfig(filename=LOG_FILE, level=LOG_LEVEL, 
                    format="%(asctime)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)

class Scan_serials(ModalScreen):
    """
    This class represents a screen for scanning or typing serial numbers of payment terminals. 
    It handles user input, validates serial numbers, checks their existence in PaxStore, 
    and allows registration of new terminals.
    """

    BINDINGS = [
        ("escape", "app.pop_screen", "BACK"),  # Bind 'escape' key to go back to the previous screen
        ("0000", "", "SUBMIT"),  # Bind '0000' input to finish serial number entry
        ("BKSPC", "", "Delete Previous item")   # Bind 'BKSPC' input to delete the last entered serial number
    ]

    def __init__(self):
        """
        Initializes the Scan_serials screen.
        """
    def __init__(self):
        self.order_of_input = [] # list of all input in order of input
        self.serialValidator = SerialNoValidator()  # Create an instance of the validator
        self.exceptions = [] # list of all terminals not found in PaxStore
        self.ops = apiPaxFunctions() # Instance of apiPaxFunctions for PaxStore operations
        self.logger = logger
        super().__init__()
        logger.debug("Scan_serials initialized") # Log initialization


    def compose(self) -> ComposeResult:
        """
        Composes the layout of the screen.
        """
        yield Header(name='PaxTools')  # Add a header with the title "PaxTools"
        yield Static("SCAN OR TYPE SERIAL NUMBER. Type 0000 to complete. Type BKSPC to delete previously scanned serial number:")  # Add a static label for instructions
        yield Input(placeholder="S/N", validators=[self.serialValidator])  # Add an input field for serial numbers with validation
        yield Footer()  # Add a footer to the screen

    @on(Input.Submitted)  # Decorator to trigger this function when Input is submitted
    @work  # Decorator to run this function as a background task
    async def update_serial_list(self):
        """
        Handles the submitted serial number input.
        """
        user_input = self.query_one(Input)  # Get the value from the Input field
        self.order_of_input.append(user_input.value)  # Add the input to the order_of_input list
        serialNo = user_input.value  # Assign the input value to serialNo
        self.mount(Static(str(user_input.value)))  # Display the entered serial number on the screen
        # Handle special inputs
        if user_input.value == "BKSPC":  # If input is "BKSPC", remove the last entry from order_of_input
            self.order_of_input.pop()
            self.order_of_input.pop() # list.pop is called twice due to idiosyncratic logic of the Textual Library. It needs to be there
        if ":" in user_input.value:  # If input contains ":", remove the  entry from order_of_input and produce a bell sound
            self.order_of_input.pop()
            self.app.bell()
            logger.warning(f"Invalid character ':' found in input: {user_input.value}")
        if user_input.value == "0000":  # If input is "0000", disable the input field, produce a bell sound, and proceed to check PaxStore
            self.disabled = True
            self.app.bell()
            self.order_of_input.pop()
            logger.info("Input finished (0000 entered). Starting PaxStore check.")
            # Check if the entered serial numbers exist in PaxStore
            check = PaxStoreChecker(self.order_of_input)
            if check.not_in_paxStore:  # If some terminals are not found in PaxStore
                logger.warning(f"Terminals not in PaxStore: {stringify_list(check.not_in_paxStore)}")
                if await self.app.push_screen_wait(Confirm_Screen(f"These Terminals are not registered: {stringify_list(check.not_in_paxStore)}\nDo you want to register now?")):  # Ask the user if they want to register the missing terminals
                    logger.info("User chose to register missing terminals.")
                    adder = NA_Handler(check.not_in_paxStore)  # Handle the registration of new terminals
                    if adder.exceptions_list:  # If there are exceptions during registration
                        logger.error(f"Exceptions during registration: {stringify_list(adder.exceptions_list)}")
                        self.exceptions.extend(exception for exception in adder.exceptions_list)  # Add the exceptions to the exceptions list
                        if await self.app.push_screen_wait(Confirm_Screen(f"The following can not be added to the PaxStore\n{stringify_list(adder.exceptions_list)}\n Please escalate to Eval 2. Please choose:", "Remove", "Replace")):  # Ask the user to either remove or replace the problematic terminals
                            logger.info("User chose to replace exceptions.")
                            for exception in self.exceptions:  # If the user chooses to replace the excepted terminal with different unit
                                replace = await self.app.push_screen_wait(ReplaceTerminal(exception))  # Get the replacement serial number from the user
                                index = self.order_of_input.index(exception)  # Find the index of the exception in the order_of_input list
                                self.order_of_input[index] = replace  # Replace the exception with the new serial number
                                self.app.notify(str(f'{exception} replaced with {replace}'))  # Notify the user about the replacement
                                logger.info(f"Replaced {exception} with {replace}")
                        else:  # If the user chooses to remove
                            logger.warning(f"User chose not to register missing terminals:{stringify_list(check.not_in_paxStore)}")
                            self.app.push_screen(Confirm_Screen(f"Please remove these terminals before continuing \n{stringify_list(check.not_in_paxStore)}"))  # Instruct the user to remove the problematic terminals
                    self.app.notify(str(adder.terminal_data))  # Notify the user about the added terminals
                else:  # If the user doesn't want to register the missing terminals
                    logger.warning(f"User chose not to register missing terminals:{stringify_list(check.not_in_paxStore)}")
                    self.app.push_screen(Confirm_Screen(f"Please remove these terminals before continuing \n{stringify_list(check.not_in_paxStore)}"))  # Instruct the user to remove the missing terminals
                    self.exceptions.extend(serial for serial in check.not_in_paxStore)  # Add the missing terminals to the exceptions list
            # Filter the order_of_input list to remove exceptions
            final_list = [serial for serial in self.order_of_input if serial not in self.exceptions]
            self.exceptions.clear()  # Clear the exceptions list
            logger.info(f"Final list of serials: {stringify_list(final_list)}")
            # Proceed with connecting to the network and opening PaxStore on the terminals
            if await self.app.push_screen_wait(Confirm_Screen("Please connect to network and open PaxStore on terminals")):
                self.group = await self.ops.startPaxGroup(final_list)  # Start a PaxGroup with the valid serial numbers
                # Check for accessories and their registration in PaxStore
                if self.group['accessory'].any():
                    check2 = PaxStoreChecker(self.group['accessory'].dropna())
                    if check2.not_in_paxStore:
                        logger.warning(f"Accessories not in PaxStore: {stringify_list(check2.not_in_paxStore)}")
                        if await self.app.push_screen_wait(Confirm_Screen(f"These Terminals are not registered: {stringify_list(check2.not_in_paxStore)}\nDo you want to register now?")):
                            logger.info("User chose to register missing accessories.")
                            adder2 = NA_Handler(check2.not_in_paxStore)
                            if adder2.exceptions_list:
                                logger.error(f"Exceptions during accessory registration: {stringify_list(adder2.exceptions_list)}")
                                if await self.app.push_screen_wait(Confirm_Screen(f"The following can not be added to the PaxStore\n{stringify_list(adder2.exceptions_list)}\n Please escalate to Eval 2.")):
                                    pass  # Handle exceptions for accessories (currently just passes)
                self.app.notify(str(self.group))  # Notify the user about the group details
                logger.info(f"Group details: {self.group}")
                self.app.push_screen(FunctionsScreen(pd.DataFrame(self.group),logger))  # Push the FuctionsScreen with the group data
        user_input.clear()  # Clear the input field

        
class scan_v2(App):

    def on_mount(self) -> None:
         self.push_screen(Scan_serials())
         

if __name__ == "__main__":
    app = scan_v2()
    app.run()

