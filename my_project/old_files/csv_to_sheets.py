import os.path
import csv

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = "1W6C6-jNtSEXQwdFqZuNxDABtvTu4eLDSYFaq4Xhpnj8"
RANGE_NAME = "testing!A:Z"

def update_google_sheet():
  """Shows basic usage of the Sheets API.
  Prints values from a sample spreadsheet.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("../my_project/utils/token.json"):
    creds = Credentials.from_authorized_user_file("../my_project/utils/token.json", SCOPES)
    print(creds)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "../my_project/utils/credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("./token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("sheets", "v4", credentials=creds)

    # Read CSV file and convert to list of lists
    csv_file_path = f"../data/production/csv_export.csv"
    data = []
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row)


    # Clear data to Google Sheet
    service.spreadsheets().values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
    ).execute()
    print("working")
    # Upload data to Google Sheet
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption='USER_ENTERED',
        body={'values': data}
    ).execute()
  except HttpError as err:
    print(err)


