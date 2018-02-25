# # Imports for calendar writing
from apiclient import discovery
import google_auth_httplib2

# import httplib2
#
# # Imports for credential acquisition
# import os
# from oauth2client import client
# from oauth2client import tools
# from oauth2client.file import Storage
#
# CLIENT_SECRET_FILE = '_junk/client_id.json'
# SCOPES = 'https://www.googleapis.com/auth/calendar'
#
#
# def get_credentials(name):
#     """Gets valid user credentials from storage.
#
#     If nothing has been stored, or if the stored credentials are invalid,
#     the OAuth2 flow is completed to obtain the new credentials.
#
#     Returns:
#         Credentials, the obtained credential.
#     """
#
#     try:
#         import argparse
#         flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
#     except ImportError:
#         flags = None
#
#     home_dir = os.path.expanduser('~')
#     credential_dir = os.path.join(home_dir, '.credentials')
#     if not os.path.exists(credential_dir):
#         os.makedirs(credential_dir)
#     credential_path = os.path.join(credential_dir, f'{name}.json')
#
#     store = Storage(credential_path)
#     credentials = store.get()
#     if not credentials or credentials.invalid:
#         flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
#         flow.user_agent = name
#         if flags:
#             credentials = tools.run_flow(flow, store, flags)
#         else: # Needed only for compatibility with Python 2.6
#             credentials = tools.run(flow, store)
#         print('Storing credentials to ' + credential_path)
#     return credentials


# Import for event dating
import datetime
# Imports for authentication
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class CalendarHandler:
    def __init__(self, client_secrets_file, user_token_file):

        flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes=SCOPES,
                                                         redirect_uri='urn:ietf:wg:oauth:2.0:oob')
        self.credentials = flow.run_console()
        self.session = flow.authorized_session()

    def _add_event(self, event_details):
        """ Function for handling calendar even creation"""
        # Retrieve today's date
        now = datetime.date.today().isoformat()
        event_date = {
            "start": {"date": now},
            "end": {"date": now},
            "transparency": "transparent"
        }
        # Combine the event details handed to us, with the date we generated
        event_data = {**event_date, **event_details}

        service = discovery.build('calendar', 'v3', credentials=self.credentials)
        event = service.events().insert(calendarId=self.CALENDAR_ID, body=event_data).execute()
        return event['htmlLink']

    def add_shipped(self, subscription_details, scraped_info):
        """ Function for adding 'shipped issue' event to calendar"""
        event = {
            "summary": "".join([subscription_details["shortname"], " - SHIPPED - ",
                                scraped_info["shipped"], "/", scraped_info["total"]]),
            "location": "".join(["#", subscription_details["startAt"] + scraped_info["shipped"]]),
            "description": scraped_info["title"]
        }
        self._add_event(event)

    def add_processing(self, subscription_details, scraped_info):
        """ Function for adding 'in-processing issue' event to calendar"""
        processing_count = scraped_info["shipped"] + scraped_info["processing"]
        event = {
            "summary": "".join([subscription_details["shortname"], " - PROCESSING - ",
                                processing_count, "/", scraped_info["total"]]),
            "location": "".join(["#", subscription_details["startAt"] + processing_count]),
            "description": scraped_info["title"]
        }
        self._add_event(event)


'''
Event Format:
Summary: `shortname - STATUS - issueCount/totalIssues`
Location: `#issueNo`
Description: `title`
'''