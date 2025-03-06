import logging
import pandas as pd
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Button, Header, Footer
from textual import on, work
from textual.containers import Container, VerticalScroll
from .DFTable import DataFrameTable
from .ti_labels_iccid import create_pdf
from .confmscn import Confirm_Screen


class CloseGroupScreen(Screen): 

    BINDINGS = [("escape", "app.pop_screen", "BACK")]

    def __init__(self, df: pd.DataFrame, logger: logging):
        
        self.df = df
        self.logger = logger
        super().__init__()
        self.logger.debug("Close Group screen initialized") #log initialization

    def compose(self) -> ComposeResult:

        yield Header(name = "PaxTools");
        with Container(id = )