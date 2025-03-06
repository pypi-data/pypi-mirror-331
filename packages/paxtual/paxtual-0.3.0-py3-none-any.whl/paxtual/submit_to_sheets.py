import gspread
from google.oauth2 import service_account
import os
import pandas as pd

# Get the service account file path from the environment variable
SERVICE_ACCOUNT_FILE = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

# Replace with the name or URL of your Google Sheet
SHEET_NAME = 'new'

# Replace with the name of the wsorksheet you want to use
WORKSHEET_NAME = 'Sheet1'

def format_dataframe(records: dict):
    drop = ["id","tid","merchantName", "imei", "screenResolution", "language", "ip", "macAddress"]
    df = pd.DataFrame(records).drop(columns=drop, axis=1)
    data = df.values.tolist()
    return data

def add_production_data(data: list):
    """Adds production data to a Google Sheet using credentials from an environment variable.

    Args:
        data: A list of lists, where each inner list represents a row of data.
    """
    if not SERVICE_ACCOUNT_FILE:
        print("Error: GOOGLE_APPLICATION_CREDENTIALS environment variable not set.")
        return

    try:
        # Authenticate with Google Sheets
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        gc = gspread.Client(auth=credentials)
        print(SHEET_NAME)
        # Open the Google Sheet
        sheet = gc.open_by_key("1g25m-ZEtkk_gsAevSdLtq-m7JqLK15jZS52ZbpvsESM")

        # Open the worksheet
        worksheet = sheet.worksheet(WORKSHEET_NAME)
        try:
            cell_value = worksheet.acell('A1').value
            print(f"Value of cell A1: {cell_value}")
        except Exception as e:
            print(f"Error during test read: {e}")

        # Find the next available row
        next_row = len(worksheet.get_all_values()) + 1

        # Add the data to the worksheet
        worksheet.append_rows(data, value_input_option='USER_ENTERED', table_range=f'A{next_row}')

        print(f"Data added to worksheet '{WORKSHEET_NAME}' successfully.")

    except FileNotFoundError:
        print(f"Error: Service account file not found at {SERVICE_ACCOUNT_FILE}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Example production data (replace with your actual data)
    records = [{'id': 1665857230995561, 'name': 'TR_E600M', 'tid': 'GU4G2FLZ', 'serialNo': '2270007929', 'status': 'A', 'merchantName': 'North American Bancard', 'modelName': 'E600M', 'resellerName': 'Production', 'createdDate': 1741027429000, 'lastActiveTime': 1741038806000, 'pn': 'E600M-A9400-1429-5C0-EA', 'osVersion': '10', 'imei': '356421170093965', 'screenResolution': '600px * 1024px', 'language': 'English', 'ip': '192.168.44.1,192.168.2.103', 'timeZone': 'GMT -05:00', 'macAddress': '22:CD:B8:06:FF:4B', 'iccid': 'nan', 'cellid': 'nan', 'location': 'nan', 'remark': 'nan', 'accessory': '2400008453'}, {'id': 1665857230995529, 'name': 'TR_E600M', 'tid': 'JV8ZDNX2', 'serialNo': '2270006216', 'status': 'A', 'merchantName': 'North American Bancard', 'modelName': 'E600M', 'resellerName': 'Production', 'createdDate': 1741027429000, 'lastActiveTime': 1741038806000, 'pn': 'E600M-A9400-1429-5C0-EA', 'osVersion': '10', 'imei': '356421170080889', 'screenResolution': '600px * 1024px', 'language': 'English', 'ip': '192.168.44.1,192.168.2.101', 'timeZone': 'GMT -05:00', 'macAddress': '3E:82:D4:47:2F:AA', 'iccid': 'nan', 'cellid': 'nan', 'location': 'nan', 'remark': 'nan', 'accessory': '2400007593'}, {'id': 1665857230995527, 'name': 'TR_A920Pro', 'tid': 'O7T1KQJO', 'serialNo': '1850403116', 'status': 'A', 'merchantName': 'North American Bancard', 'modelName': 'A920Pro', 'resellerName': 'A920 Config', 'createdDate': 1741027429000, 'lastActiveTime': 1741028122000, 'pn': 'A920Pro-0AW-RD5-10EA', 'osVersion': '8.1.0', 'imei': '359063102828055', 'screenResolution': '720px * 1440px', 'language': 'English', 'ip': '10.20.46.20', 'timeZone': 'GMT -05:00', 'macAddress': 'F4:02:23:54:40:81', 'iccid': 'nan', 'cellid': 'nan', 'location': 'nan', 'remark': 'nan', 'accessory': None}, {'id': 1490297880055525, 'name': '3130034368425', 'tid': 'YXHVCIU0', 'serialNo': '1340027046', 'status': 'S', 'merchantName': 'North American Bancard', 'modelName': 'E700', 'resellerName': 'Production', 'createdDate': 1657314207000, 'lastActiveTime': 1657314184000, 'pn': 'E700-A8200-1431-503-EA', 'osVersion': '7.1.2', 'imei': '861473040422310', 'screenResolution': '1920px * 1080px', 'language': 'English', 'ip': '192.168.44.1', 'timeZone': 'GMT -08:00', 'macAddress': '20:50:E7:7F:36:B2', 'iccid': '89011703278973490207', 'cellid': '192421594', 'location': 'nan', 'remark': 'nan', 'accessory': '1140127379'}, {'id': 1483730570971731, 'name': '3130033681422', 'tid': 'PS2L1O6L', 'serialNo': '1340019089', 'status': 'S', 'merchantName': 'North American Bancard', 'modelName': 'E700', 'resellerName': 'Production', 'createdDate': 1654182670000, 'lastActiveTime': 1654182660000, 'pn': 'E700-A8200-1431-503-EA', 'osVersion': '7.1.2', 'imei': '861473040132141', 'screenResolution': '1920px * 1080px', 'language': 'English', 'ip': '10.1.10.123', 'timeZone': 'GMT -04:00', 'macAddress': 'D4:9C:DD:99:17:D0', 'iccid': 'nan', 'cellid': 'nan', 'location': 'West Dennis,  MA  02670', 'remark': '', 'accessory': '1140111280'}, {'id': 1665857230995497, 'name': 'Q10', 'tid': 'P8DESILN', 'serialNo': '2400008453', 'status': 'A', 'merchantName': 'North American Bancard', 'modelName': 'Q10A', 'resellerName': 'Production', 'createdDate': 1741027429000, 'lastActiveTime': 1741038806000, 'pn': 'nan', 'osVersion': 'nan', 'imei': 'nan', 'screenResolution': 'nan', 'language': 'nan', 'ip': 'nan', 'timeZone': 'nan', 'macAddress': 'nan', 'iccid': 'nan', 'cellid': 'nan', 'location': 'nan', 'remark': 'nan', 'accessory': 'nan'}, {'id': 1665857230995495, 'name': 'Q10', 'tid': 'P86K5PXP', 'serialNo': '2400007593', 'status': 'A', 'merchantName': 'North American Bancard', 'modelName': 'Q10A', 'resellerName': 'Production', 'createdDate': 1741027429000, 'lastActiveTime': 1741038806000, 'pn': 'nan', 'osVersion': 'nan', 'imei': 'nan', 'screenResolution': 'nan', 'language': 'nan', 'ip': 'nan', 'timeZone': 'nan', 'macAddress': 'nan', 'iccid': 'nan', 'cellid': 'nan', 'location': 'nan', 'remark': 'nan', 'accessory': 'nan'}, {'id': 1490298578407141, 'name': '3130034368425', 'tid': 'EFXI98ZL', 'serialNo': '1140127379', 'status': 'A', 'merchantName': 'North American Bancard', 'modelName': 'Q20L', 'resellerName': 'Production', 'createdDate': 1657314540000, 'lastActiveTime': 1657314516000, 'pn': 'nan', 'osVersion': 'nan', 'imei': 'nan', 'screenResolution': 'nan', 'language': 'nan', 'ip': 'nan', 'timeZone': 'nan', 'macAddress': 'nan', 'iccid': 'nan', 'cellid': 'nan', 'location': 'nan', 'remark': 'nan', 'accessory': 'nan'}, {'id': 1483731470649939, 'name': '3130033681422', 'tid': 'RX9DIGRV', 'serialNo': '1140111280', 'status': 'A', 'merchantName': 'North American Bancard', 'modelName': 'Q20L', 'resellerName': 'Production', 'createdDate': 1654183098000, 'lastActiveTime': 1654183089000, 'pn': 'nan', 'osVersion': 'nan', 'imei': 'nan', 'screenResolution': 'nan', 'language': 'nan', 'ip': 'nan', 'timeZone': 'nan', 'macAddress': 'nan', 'iccid': 'nan', 'cellid': 'nan', 'location': 'West Dennis,  MA  02670', 'remark': '', 'accessory': 'nan'}]
    production_data_no_headers = format_dataframe(records)
    #add_production_data(production_data)
    add_production_data(production_data_no_headers) #example of subsequent runs.