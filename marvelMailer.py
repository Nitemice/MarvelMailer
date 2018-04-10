"""
Marvel Mailer

Tracks Marvel subscriptions by keeping an eye on issue processing and shipping.
"""

__version__ = "2.1"
__author__ = "Nitemice"
__app_name__ = "MarvelMailer"


# Import packages for reading config
import argparse
import json
import sys
import os
# Import requesting & scraping libraries
import requests
from bs4 import BeautifulSoup
# Import data-storage location package
from appdirs import AppDirs
# Import notifier & calendar handler packages
from notifier import Notifier, OutputMethodError, Verbosity
from calendar_handler import CalendarHandler

# Setup config file variables
CONFIG_FILE = "config.json"
config = {}

# Setup command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("config_file", nargs="?", type=argparse.FileType("r"),
                    default=CONFIG_FILE, help="config file, in JSON format")
parser.add_argument("--version", action="store_true", help="print version")
verbosity_group = parser.add_mutually_exclusive_group()
verbosity_group.add_argument("-q", "--quiet", action="store_true", help="quiet output")
verbosity_group.add_argument("-s", "--silent", action="store_true", help="silent output")
args = parser.parse_args()

# Check if they just want a version number
if args.version:
    print(__version__)
    sys.exit(0)

# Load the config file
try:
    config = json.load(args.config_file)
except FileNotFoundError as e:
    sys.exit(e)

# Set verbosity for notifier
if args.silent:
    verbosity = Verbosity.silent
elif args.quiet:
    verbosity = Verbosity.quiet
else:
    verbosity = Verbosity.normal

# Setup notification system
if "notifier" in config:
    try:
        notifier = Notifier(config=config["notifier"], verbosity=verbosity)
    except OutputMethodError as e:
        sys.exit(e.message)
else:
    notifier = Notifier(verbosity=verbosity)

# Setup directory finder
dirs = AppDirs(__app_name__, __author__)

# Setup calendar handler
if "secrets" not in config or "client_secret_file" not in config["secrets"]:
    notifier.error("Client secret file not specified.")
    sys.exit(1)
cal = CalendarHandler(config["secrets"]["client_secret_file"], dirs.user_cache_dir,
                      config["secrets"]["calendar_id"], notifier)

# == Scrape website ==
# Define structure for storing scraped values
scraped_subs = []
scraped_subs_titles = []
URL = "https://subscriptions.marvel.com/accounts/myaccount.asp"

# Create cookie header, to get past the authentication
if "secrets" not in config or "marvel_cookie" not in config["secrets"]:
    notifier.error("Marvel cookie not found.")
    sys.exit(1)
request_headers = {"Cookie": config["secrets"]["marvel_cookie"]}

# Request page with cookie and feed it to BeautifulSoup
r = requests.get(URL, headers=request_headers)
soup = BeautifulSoup(r.text, "html.parser")

# Check if we successfully got the 'My Account' page
if not soup.find("div", string="Customer Addresses"):
    notifier.error("Failed to get logged in 'My Account' page.")
    sys.exit(2)

# Find the issue status table header
subscriptions_table_heading = soup.find("div", string="Active Titles")
if not subscriptions_table_heading:
    notifier.error("Failed to get logged in 'My Account' page.")
    sys.exit(2)
# Get the subscriptions table's div
subscriptions_table = subscriptions_table_heading.find_next("table")

# Loop over all the rows, and store all the values
for row in subscriptions_table.find_all("tr", recursive=False):
    # Skip the table header row
    if "bold" in row.td.attrs["class"]:
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
        notifier.notify("Total doesn't add up for " + subscription_info["title"])
        notifier.notify(json.dumps(subscription_info))

    # Store the title for later
    scraped_subs_titles.append(subscription_info["title"])

    scraped_subs.append(subscription_info)

# == Compare previous subscriptions ==
SAVED_SUBS_FILE = "subscriptions.json"

# Work out where the previous subscriptions file will be
if "subscription_file" in config:
    subs_filename = config["subscription_file"]
else:
    # Lookup the default location
    data_dir = dirs.user_data_dir
    if not os.path.lexists(data_dir):
        os.makedirs(data_dir, exist_ok=True)

    subs_filename = os.path.join(data_dir, SAVED_SUBS_FILE)

# Load the previous subscriptions file
saved_subs = {}
try:
    with open(subs_filename) as json_file:
        saved_subs = json.load(json_file)
except FileNotFoundError:
    notifier.notify("Previous subscription data not found. New file will be created.")
    saved_subs = scraped_subs

# Compare old and new values to see if any of these values are new/updated
if saved_subs != scraped_subs:
    notifier.notify("Change detected")  # TODO Remove?
    for new_sub in scraped_subs:

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
            notifier.notify("New subscription found: %(title)s" % new_sub)

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
            notifier.error("Subscription details missing for %(title)s.\n"
                           "Using default values (short name = title, start from issue #1)."
                           % subscription_details)

        # TODO - handle multiple shipped/processing at same time
        # Create an event to indicate a new issue has been shipped
        if old_sub["shipped"] < new_sub["shipped"]:
            cal.add_shipped(subscription_details, new_sub)
            if "expected_delivery_time" in config:
                cal.add_estimated_arrival(subscription_details, new_sub,
                                          config["expected_delivery_time"])

            # If an issue has shipped, but the processing count hasn't
            # decreased, a new issue must be in processing
            if new_sub["processing"] > 0 and old_sub["processing"] <= new_sub["processing"]:
                cal.add_processing(subscription_details, new_sub)

        # Create an event to indicate a new issue is being processed
        if old_sub["processing"] < new_sub["processing"]:
            cal.add_processing(subscription_details, new_sub)

# == Save to file ==
# Combine the new subscription data with the old, so nothing is lost
missing_subs = [x for x in saved_subs if x["title"] not in scraped_subs_titles]

# Save the new issue statuses
with open(subs_filename, "w") as outfile:
    json.dump(scraped_subs + missing_subs, outfile)
