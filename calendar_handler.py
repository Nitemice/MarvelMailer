# Import for event dating
import datetime
# Import for preserving and restoring credentials
import pickle
import os
# Imports for authentication
from google_auth_oauthlib.flow import *
# Imports for calendar writing
import google_auth_httplib2
from apiclient import discovery

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class CalendarHandler:
    """
    CalendarHandler

    Handles authentication and adding events to the calendar.
    """

    def __init__(self, client_secrets_file, user_creds_folder, calendar_id):
        """
        Authenticates the user and sets up the credentials for adding events.

        Check if there are any stored user credentials, and if so refresh and
        use them. Otherwise, prompt the user to authenticate via a web address.
        """
        self.calendar_id = calendar_id
        # Check if we have a set of pickled credentials
        creds_file = os.path.join(user_creds_folder, "credentials.pkl")
        try:
            with open(creds_file, "rb") as pkl_file:
                credentials = pickle.load(pkl_file)
        except FileNotFoundError:
            os.makedirs(user_creds_folder, exist_ok=True)
            credentials = False

        if not credentials or not credentials.valid:
            # Credentials don't exist, or are invalid, so we need to generate some new ones
            flow = InstalledAppFlow. \
                from_client_secrets_file(client_secrets_file, scopes=SCOPES,
                                         redirect_uri='urn:ietf:wg:oauth:2.0:oob')
            credentials = flow.run_console()
        else:
            # Refresh the credentials to make sure they last
            request = google.auth.transport.requests.Request()
            credentials.refresh(request)

        self.credentials = credentials

        # Pickle the credentials for next time
        with open(creds_file, 'wb') as pkl_file:
            pickle.dump(credentials, pkl_file)

    def _add_event(self, event_details):
        """Create and add a calendar event, with today's date."""
        # Retrieve today's date
        now = datetime.date.today().isoformat()
        event_date = {
            "start": {"date": now},
            "end": {"date": now},
            "transparency": "transparent"
        }
        # Combine the event details handed to us, with the date we generated
        event_data = {**event_date, **event_details}

        # Dispatch it to the calendar
        service = discovery.build('calendar', 'v3', credentials=self.credentials)
        event = service.events().insert(calendarId=self.calendar_id, body=event_data).execute()
        return event['htmlLink']

    """
    Event Format:
    Summary: `shortname - STATUS - issueCount/totalIssues`
    Location: `#issueNo`
    Description: `title`
    """

    def add_shipped(self, subscription_details, scraped_info):
        """Add a 'shipped issue' event to the calendar."""
        issue_no = subscription_details["start_from"] + scraped_info["shipped"] - 1
        event = {
            "summary": (subscription_details["short_name"] + " - SHIPPED - " +
                        str(scraped_info["shipped"]) + "/" + str(scraped_info["total"])),
            "location": "#" + str(issue_no),
            "description": scraped_info["title"]
        }
        return self._add_event(event)

    def add_processing(self, subscription_details, scraped_info):
        """Add a 'in-processing issue' event to the calendar."""
        processing_count = scraped_info["shipped"] + scraped_info["processing"]
        issue_no = subscription_details["start_from"] + processing_count - 1
        event = {
            "summary": (subscription_details["short_name"] + " - PROCESSING - " +
                        str(processing_count) + "/" + str(scraped_info["total"])),
            "location": "#" + str(issue_no),
            "description": scraped_info["title"]
        }
        return self._add_event(event)
