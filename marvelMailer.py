"""
Marvel Mailer v2
Written by Nitemice
21/01/2018
Last Edited: 21/02/2018
"""

# Import packages for reading config
import json
import sys
import os
# Import scraping & requesting libraries
import requests
from bs4 import BeautifulSoup
# Import data-storage location package
from appdirs import AppDirs
# Import notifier & calendar handler packages
from notifier import Notifier, OutputMethodError
from calendar_handler import CalendarHandler

# Setup handy const values
APP_NAME = "MarvelMailer"
DEVELOPER = "Nitemice"
VERSION = 2.0

# Setup config file variables
CONFIG_FILE = "config.json"
config = {}

# Load the config file
try:
    with open(CONFIG_FILE) as json_file:
        config = json.load(json_file)
except FileNotFoundError as e:
    sys.exit(e)

# Setup notification system
if "notifier" in config:
    try:
        n = Notifier(config["notifier"])
    except OutputMethodError as e:
        sys.exit(e.message)
else:
    n = Notifier()

# Setup calendar handler
cal = CalendarHandler("_junk/client_id.json", "moo")

# == Scrape website ==
# Define structure for storing scraped values
scraped_subs = []
scraped_subs_titles = []
URL = "https://subscriptions.marvel.com/accounts/myaccount.asp"

# Create cookie header, to get past the authentication
if "secrets" not in config or "marvel_cookie" not in config["secrets"]:
    n.error("Marvel cookie not found.")
    sys.exit(1)
headers = {"Cookie": config["secrets"]["marvel_cookie"]}

# Request page with cookie and feed it to BeautifulSoup
r = requests.get(URL, headers=headers)
soup = BeautifulSoup(r.text, 'html.parser')

# Find the issue status table header
heading = soup.find("div", string="Active Titles")
# Get the table's div
table = heading.find_next("table")

# Loop over all the rows, and store all the values
for row in table.find_all("tr", recursive=False):
    # Skip the table header row
    if 'bold' in row.td.attrs['class']:
        continue
    # Parse data into dictionary
    data = row.find_all("td", recursive=False)
    subscription_info = {
        "index": int(data[0].string),
        "title": str(data[1].string),
        "total": int(data[3].string),
        "shipped": int(data[4].string),
        "processing": int(data[5].string),
        "remaining": int(data[6].string)
    }

    # Quick check that issue count adds up
    if subscription_info["total"] != \
       subscription_info["shipped"] + subscription_info["processing"] + \
       subscription_info["remaining"]:
        # It's not quite an error, but is worth noting
        n.notify("Total doesn't add up for " + subscription_info["title"])
        n.notify(json.dumps(subscription_info))

    scraped_subs.append(subscription_info)

# == Compare previous subscriptions ==
# Work out where the previous subscriptions file will be
dirs = AppDirs(APP_NAME, DEVELOPER)
data_dir = dirs.user_data_dir

# Check if the folder even exists, and if not, create it
if not os.path.lexists(data_dir):
    os.makedirs(data_dir, exist_ok=True)

SAVED_SUBS_FILE = "subscriptions.json"
subs_filename = os.path.join(data_dir, SAVED_SUBS_FILE)

# Load the previous subscriptions file
saved_subs = {}
try:
    with open(subs_filename) as json_file:
        saved_subs = json.load(json_file)
except FileNotFoundError:
    n.notify("Previous subscription data not found. New file will be created.")
    saved_subs = scraped_subs

# Compare old and new values to see if any of these values are new/updated
if saved_subs != scraped_subs:
    n.notify("Change detected")  # TODO Remove?
    for new_sub in scraped_subs:
        # Store the title for later
        scraped_subs_titles.append(new_sub["title"])

        # Retrieve the matching saved subscription
        old_sub = [x for x in saved_subs if x["title"] == new_sub["title"]]
        if len(old_sub) == 1:
            # The single subscription is the one we're looking for
            old_sub = old_sub[0]
        elif len(old_sub) > 1:
            # Ignore old, complete subscriptions with the same name
            old_sub = [x for x in old_sub if x["total"] != x["shipped"]][0]
        else:
            # This must be a new subscription
            n.notify("New subscription found: %(title}s" % {"title": new_sub["title"]})

        # Retrieve the subscription details from the config file
        subscription_details = [x for x in config["subscriptions"]
                                if x["title"] == new_sub["title"]]
        if len(subscription_details) >= 1:
            # Just use the first set of details we find
            subscription_details = subscription_details[0]
        else:
            # Subscription details not given
            subscription_details = {"title": new_sub["title"],
                                    "short_name": new_sub["title"],
                                    "start_from": 1}
            n.error("Subscription details missing for %(title)s.\n"
                    "Using default values (short name = title, start_from = 1)."
                    % subscription_details)

        # TODO - handle multiple shipped/processing at same time
        # Create an event to indicate a new issue has been shipped
        if old_sub["shipped"] < new_sub["shipped"]:
            cal.add_shipped(subscription_details, new_sub)

            # If an issue has shipped, but the processing count hasn't
            # decreased, a new issue must be in processing
            if new_sub["processing"] > 0 and old_sub["processing"] <= new_sub["processing"]:
                cal.add_processing(subscription_details, new_sub)

        # Create an event to indicate a new issue is being processed
        if old_sub["processing"] < new_sub["processing"]:
            cal.add_processing(subscription_details, new_sub)

# Combine the new subscription data with the old, so nothing is lost
missing_subs = [x for x in saved_subs if x["title"] not in scraped_subs_titles]

# Save the new issue statuses
with open(subs_filename, 'w') as outfile:
    json.dump(scraped_subs + missing_subs, outfile)
