"""
Marvel Mailer v2
Written by Nitemice
21/01/2018
Last Edited: 21/02/2018
"""

# Import packages for reading config
import json
import sys
# Import notifier package
from notifier import Notifier, OutputMethodError
# Import scraping & requesting libraries
import requests
from bs4 import BeautifulSoup
# Import data-storage location package
from appdirs import AppDirs

# Setup handy const values
APP_NAME = "MarvelMailer"
DEVELOPER = "Nitemice"
VERSION = 2.0

# Setup config file variables
CONFIG_FILE = "config.json"
config = []

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

# Create cookie header, to get past the authentication
if "secrets" not in config or "marvel_cookie" not in config["secrets"]:
    n.error("Marvel cookie not found.")
    sys.exit(1)

headers = {"Cookie": config["secrets"]["marvel_cookie"]}
URL = "https://subscriptions.marvel.com/accounts/myaccount.asp"

# Define structure for storing scraped values
scraped_subs = []

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

    # Quick logic check
    if subscription_info["total"] != \
       subscription_info["shipped"] + subscription_info["processing"] + \
       subscription_info["remaining"]:
        n.notify("Total doesn't add up for " + subscription_info["title"])
        n.notify(json.dumps(subscription_info))

    scraped_subs.append(subscription_info)

# Check if any of these values are new/updated
dirs = AppDirs(APP_NAME, DEVELOPER)

filename = "issueStatus.json"
prevIssueStatus = {}
try:
    with open(filename) as json_file:
        prevIssueStatus = json.load(json_file)
except FileNotFoundError:
    n.error("File doesn't exist")
    prevIssueStatus = scraped_subs

# Compare old and new values
if prevIssueStatus != scraped_subs:
    n.notify("Change detected")
    for newIssue in scraped_subs:
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
            if newIssue["processing"] > 0 and oldIssue["processing"] == newIssue["processing"]:
                addProcessing(issueConfig, newIssue)

        # Create an event to indicate a new issue is being processed
        if oldIssue["processing"] < newIssue["processing"]:
            addProcessing(issueConfig, newIssue)

# Save the new issue statuses
with open(filename, 'w') as outfile:
    json.dump(scraped_subs, outfile)
