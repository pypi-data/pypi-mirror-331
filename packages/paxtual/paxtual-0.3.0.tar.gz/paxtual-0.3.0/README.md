# paxtual

[![PyPI - Version](https://img.shields.io/pypi/v/paxtual.svg)](https://pypi.org/project/paxtual)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/paxtual.svg)](https://pypi.org/project/paxtual)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install paxtual
```
## License

`paxtual` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## PaxTui User Guide

### Adding Terminals

### 1. Input Selection

*   **Scan or Import:**
    *   Import a list of serial numbers from a file (CSV, Excel) - _not yet functional_
    *   Scan each terminal using the scanning interface.

### 2. Adding Terminals to PaxTui

*   **Scan or Type:** Scan the terminal's serial number or manually type it in.
*   **"BKSPC" to Delete:** Type "BKSPC" to delete the last entered serial number.
*   **MAC Address:** Accidentally scanned MAC addresses are automatically removed.
*   **"0000" to Finish:** Type "0000" to finish entering serial numbers.

### 3. Registration

*   **PaxStore Check:** The interface automatically checks if terminals are registered in PaxStore.
*   **New Terminal Registration:**
    *   You'll be prompted to register unregistered terminals.
    *   The interface will attempt to add them to PaxStore.
*   **Registration Issues:**
    *   If a terminal cannot be registered:
        *   Remove the problematic terminal.
        *   Replace it with a different terminal.
        *   Add the terminal to the Eval 2 spreadsheet and place it in the Eval 2 staging area.

### 4. Network and PaxStore

*   **Connect and Open:** Connect the terminals to the network and open PaxStore on each.
    *   Ensure this is done before proceeding, especially for E-series devices, to ensure proper accessory checks.

### 5. Accessories

*   **Accessory Check:** The interface checks for associated accessories and their registration status.
*   **Accessory Registration:** You can register any unregistered accessories.

After successful registration, you'll be directed to the "Functions Screen" to perform actions on the terminals.

**Important Notes:**

*   Follow on-screen prompts.
*   Remember the special input commands ("0000" and "BKSPC").
*   Ensure terminals have stable network connectivity.


### Group Operations

This interface allows you to manage and perform actions on registered Pax terminals.

### 1. Terminal Information

*   **Table View:** A table displays key details (serial number, status, model, etc.) for each terminal.
*   **Click for Details:** Click a serial number to view detailed information in the "Terminal Details Screen".

### 2. Available Actions

*   **Available Tasks:**
    *   **Reset Group:** Resets PaxStore data to default.
    *   **Activate Group:** Activates terminals in PaxStore.
    *   **Deactivate:** Deactivates terminals in PaxStore.
    *   **Reboot Group:** Reboots terminals.
    *   **Refresh Terminal Details:** Refreshes displayed information.
    *   **Create Ticket Labels:** Generates picking ticket labels.
*   **Configuration Tasks:**
    *   **Config for PayAnywhere:** Configures terminals for PayAnywhere.
    *   **Config for BroadPOS - EPX:** Configures terminals for BroadPOS with EPX.
    *   **Config for BroadPOS - Not EPX:** Configures terminals for BroadPOS without EPX.

### 3. Performing Actions

*   Click the corresponding button to perform an action.
*   Confirm your action in the confirmation screen.
*   Ensure terminals are connected to the network and have PaxStore open.
*   Notifications will display the result of the action.
*   The table will refresh to reflect any changes.

**Important Notes:**

*   Error messages will be displayed if an error occurs.
*   Ensure stable network connectivity for actions involving PaxStore or configuration updates.
*   Pay attention to confirmation screens.
*   Use the "Terminal Details Screen" for in-depth information about a specific terminal.