#rom google_auth_oauthlib.flow import Flow
#from calendar_handler import CalendarHandler
from notifier import Notifier
from google_auth_oauthlib.flow import *
from apiclient import discovery
import google_auth_httplib2


n = Notifier()
n.notify("DUMMY running")


# # Create the flow using the client secrets file from the Google API
# # Console.
# flow = Flow.from_client_secrets_file(
#     '_junk/client_id.json',
#     scopes=['profile', 'email'],
#     redirect_uri='urn:ietf:wg:oauth:2.0:oob')
#
# # Tell the user to go to the authorization URL.
# auth_url, _ = flow.authorization_url(prompt='consent')
#
# print('Please go to this URL: {}'.format(auth_url))
#
# # The user will get an authorization code. This code is used to get the
# # access token.
# code = input('Enter the authorization code: ')
# flow.fetch_token(code=code)
#
# # You can use flow.credentials, or you can just get a requests session
# # using flow.authorized_session.
# session = flow.authorized_session()
# print(session.get('https://www.googleapis.com/userinfo/v2/me').json())
import datetime

now = datetime.date.today().isoformat()

event_data = {
            "start": {"date": now},
            "end": {"date": now},
            "transparency": "transparent",
            "summary": " - PROCESSING - "
        }

# Create the flow using the client secrets file from the Google API
# Console.
flow = InstalledAppFlow.from_client_secrets_file(
    '_junk/client_id.json',
    scopes=["https://www.googleapis.com/auth/calendar"],
    redirect_uri='urn:ietf:wg:oauth:2.0:oob')

credentials = flow.run_console()

# You can use flow.credentials, or you can just get a requests session
# using flow.authorized_session.
session = flow.authorized_session()
write(credentials.to_json())
service = discovery.build('calendar', 'v3', credentials=credentials)
event = service.events().insert(calendarId="1sdtrqskn54a5q2bfou9hk375c@group.calendar.google.com",
                                body=event_data).execute()
print(event['htmlLink'])