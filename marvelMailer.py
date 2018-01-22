'''
Marvel Mailer v1
Written by Nitemice
21/01/2018
Last Edited: 21/01/2018
'''

# Import scraping & requesting libraries
import requests
from bs4 import BeautifulSoup

# General purpose imports
import json
from win10toast import ToastNotifier

# Imports for calendar writing
import datetime
from apiclient import discovery
import httplib2

# Imports for credential acquisition
import os
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

CLIENT_SECRET_FILE = 'client_id.json'
SCOPES = 'https://www.googleapis.com/auth/calendar'

def get_credentials(name):
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """

    try:
        import argparse
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    except ImportError:
        flags = None

    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, f'{name}.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = name
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

CALENDAR_ID = ""
MARVEL_COOKIE = ""

def loadSecrets():
    global CALENDAR_ID, MARVEL_COOKIE
    try:
        with open("secrets.json") as json_file:
            secrets = json.load(json_file)
            CALENDAR_ID = secrets["CALENDAR_ID"]
            MARVEL_COOKIE = secrets["MARVEL_COOKIE"]
    except FileNotFoundError:
        pass
    return

def loadConfig():
    try:
        with open("config.json") as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        pass
    return

def addEvent(summary, location, description):
    ''' Function for handling calendar even creation '''
    now = datetime.date.today().isoformat()
    event = {
      'summary': f'{summary}',
      'location': f'{location}',
      'description': f'{description}',
      'start': {
        'date': f'{now}'
      },
      'end': {
        'date': f'{now}'
      },
      'transparency': 'transparent'
    }

    credentials = get_credentials("marvelMailer")
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    event = service.events().insert(calendarId = CALENDAR_ID,
                                    body = event).execute()
    print(f"Event created: {event['htmlLink']}")
    return

'''
Event Format:
Summary: `shortname - STATUS - issueCount/totalIssues`
Location: `#issueNo`
Description: `title`
'''

def addShipped(issueConfig, issueInfo):
    ''' Function for adding 'shipped issue' event to calendar  '''
    summary = f'{issueConfig["shortname"]} - SHIPPED - {issueInfo["shipped"]}/{issueInfo["total"]}'
    location = f'#{issueConfig["startAt"] + issueInfo["shipped"]}'
    description = issueInfo["title"]
    addEvent(summary, location, description)
    return


def addProcessing(issueConfig, issueInfo):
    ''' Function for adding 'in-processing issue' event to calendar  '''
    processingCount = issueInfo["shipped"] + issueInfo["processing"]
    summary = f'{issueConfig["shortname"]} - PROCESSING - {processingCount}/{issueInfo["total"]}'
    location = f'#{issueConfig["startAt"] + processingCount}'
    description = issueInfo["title"]
    addEvent(summary, location, description)
    return


print("Marvel Mailer v1")

# Used for raising errors
toaster = ToastNotifier()

loadSecrets()

# Define structure for storing values we scrape
issueStatus = []

# Load the config file, if it exists
config = loadConfig()

# Create cookie header, to get past the authentication
#headers = {"Cookie": "ASPSESSIONIDAQDSSSBT=HILJGCIBGHDKAOMBCONPKJEB; PHPSESSID=cnm4b9lv9a3esq2d7bvpephv65; regRefererUrl=https%3A%2F%2Fsubscriptions.marvel.com%2Faccounts%2Fmyaccount.asp%3Fnav%3D1; marvel_autologin=%7B%22username%22%3A%22NItemice%22%2C%22loginDate%22%3A%222018-01-20+20%3A45%3A36%22%2C%22signature%22%3A%22fd4bf305f1fa63e2917f79b544c977f9e531eb8f64625597bee186987ec9629fcf60110f5439e5a17afddd75966632b97deacfec1033611bdd09adcaaddf7e81%22%7D; mus[is_l]=1; mus[is_m]=0; mus[is_i]=0"}
headers = {"Cookie": MARVEL_COOKIE}
url = "https://subscriptions.marvel.com/accounts/myaccount.asp"

# Request page with cookie
r = requests.get(url, headers = headers)
# print r.text

# Feed it to BeautifulSoup
soup = BeautifulSoup(r.text, 'html.parser')

# Find the issue status table header
heading = soup.find("div", string="Active Titles")
# Get the table's div
table = heading.find_next("table")

# Loop over all the rows, and store all the values
for row in table.find_all("tr", recursive=False):
    # Ship the table header row
    if 'bold' in row.td.attrs['class']:
        continue
    # Parse data into dictionary
    data = row.find_all("td", recursive=False)
    issueInfo = {}
    issueInfo["index"] = int(data[0].string)
    issueInfo["title"] = str(data[1].string)
    issueInfo["total"] = int(data[3].string)
    issueInfo["shipped"] = int(data[4].string)
    issueInfo["processing"] = int(data[5].string)
    issueInfo["remaining"] = int(data[6].string)

    # Quick logic check
    if issueInfo["total"] != \
       issueInfo["shipped"] + issueInfo["processing"] + issueInfo["remaining"]:
        toaster.show_toast("ERROR",
                           "Total doesn't add up for " + issueInfo["title"])

    issueStatus.append(issueInfo)

# Check if any of these values are new/updated
filename = "issueStatus.json"
prevIssueStatus = {}
try:
    with open(filename) as json_file:
        prevIssueStatus = json.load(json_file)
except FileNotFoundError:
    toaster.show_toast("ERROR", "File doesn't exist")
    prevIssueStatus = issueStatus

# Compare old and new values
if prevIssueStatus != issueStatus:
    toaster.show_toast("", "Change detected")
    for newIssue in issueStatus:
        # Retrieve the matching previous values
        oldIssue = \
            [x for x in prevIssueStatus if x["title"] == newIssue["title"]][0]

        # Retrieve issue config
        issueConfig = [x for x in config if x["title"] == newIssue["title"]][0]

        # Create an event to indicate a new issue has been shipped
        if oldIssue["shipped"] < newIssue["shipped"]:
            addShipped(issueConfig, newIssue)

            # If an issue has shipped, but the processing count hasn't
            # decreased, a new issue must be in processing
            if newIssue["processing"] > 0 and \
               oldIssue["processing"] == newIssue["processing"]:
                addProcessing(issueConfig, newIssue)

        # Create an event to indicate a new issue is being processed
        if oldIssue["processing"] < newIssue["processing"]:
            addProcessing(issueConfig, newIssue)

# Save the new issue statuses
with open(filename, 'w') as outfile:
    json.dump(issueStatus, outfile)