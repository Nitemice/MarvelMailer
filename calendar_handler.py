# # Imports for calendar writing
# import datetime
# from apiclient import discovery
# import httplib2
#
# # Imports for credential acquisition
# import os
# from oauth2client import client
# from oauth2client import tools
# from oauth2client.file import Storage
#
# CLIENT_SECRET_FILE = 'client_id.json'
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
#
#
# def addEvent(summary, location, description):
#     """ Function for handling calendar even creation """
#     now = datetime.date.today().isoformat()
#     event = {
#       'summary': f'{summary}',
#       'location': f'{location}',
#       'description': f'{description}',
#       'start': {
#         'date': f'{now}'
#       },
#       'end': {
#         'date': f'{now}'
#       },
#       'transparency': 'transparent'
#     }
#
#     credentials = get_credentials("marvelMailer")
#     http = credentials.authorize(httplib2.Http())
#     service = discovery.build('calendar', 'v3', http=http)
#     event = service.events().insert(calendarId = CALENDAR_ID,
#                                     body = event).execute()
#     print(f"Event created: {event['htmlLink']}")
#     return
#
#
# '''
# Event Format:
# Summary: `shortname - STATUS - issueCount/totalIssues`
# Location: `#issueNo`
# Description: `title`
# '''


def addShipped(subscription_details, subscription_info):
    """ Function for adding 'shipped issue' event to calendar  """
    pass
#     summary = f'{subscription_details["shortname"]} - SHIPPED - {subscription_info["shipped"]}/{subscription_info["total"]}'
#     location = f'#{subscription_details["startAt"] + subscription_info["shipped"]}'
#     description = subscription_info["title"]
#     addEvent(summary, location, description)
#     return


def addProcessing(subscription_details, subscription_info):
    """ Function for adding 'in-processing issue' event to calendar  """
    pass
#     processingCount = subscription_info["shipped"] + subscription_info["processing"]
#     summary = f'{subscription_details["shortname"]} - PROCESSING - {processingCount}/{subscription_info["total"]}'
#     location = f'#{subscription_details["startAt"] + processingCount}'
#     description = subscription_info["title"]
#     addEvent(summary, location, description)
#     return
#
