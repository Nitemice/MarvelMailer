# MarvelMailer

*Tracks Marvel subscriptions by keeping an eye on issue processing and shipping*

## Overview

Marvel Mailer is a tool designed to automatically track Marvel subscriptions by
scraping the ['My Account' page](https://subscriptions.marvel.com/accounts/myaccount.asp),
and adding events to a calendar when a new issue is processed or shipped.

This is done by storing a record of each subscription's status, which is
compared with the current status on the webpage. If a difference is detected,
events are dispatched for these status changes.

## Setup

### Requirements

- Python 3.6+
- Various python packages. See `requirements.txt` for package list.

### Steps

1. Create a `client_id` secret for accessing your Google Account
    - Visit [Developer Dashboard](https://console.developers.google.com/apis/credentials?)
      and create a project
    - Add OAuth to project
    - Download `client_id.json` secret
2. Retrieve your calendar ID and Marvel Subscription cookie keys.
    - Visit [your calendar settings](https://calendar.google.com/calendar/r) and grab the URL
    - Visit the [Marvel Accoutns page](https://subscriptions.marvel.com/accounts/myaccount.asp) and 
      use the developer panel to view the `marvel_autologin` cookie header
3. Add these to `config.json` file. See 'Config File Format' for more details.
4. Optionally, define each comic subscription in `config.json`, by adding a title, shortname
   and startFrom issue number.

## Usage

Run `python marvelMailer.py`

```bash
$ python marvelMailer.py --help
Marvel Mailer v1
...
```

## Config File Format

Config files should follow the following basic structure:

```json
{
  "secrets": {
    "MARVEL_COOKIE": "<cookie keys>",
    "CALENDAR_ID": "<calendar id>"
  },
  "subscriptions": [
    {
      "title": "<comic title>",
      "shortname": "<comic shortname>",
      "startFrom": "<issue number before first sub>"
    }
  ]
}
```

- `MARVEL_COOKIE` is your authorization cookie, taken from the `COOKIE` header request to the
  'My Accounts' page.
- `CALENDAR_ID` is the unique ID of the calendar you want to add events to.
- `shortname` is a user-chosen alternative name for the comic series. This is used in event
  titles to reduce the bulk of using full titles.
- `startFrom` is the issue number of the first issue you received through the Marvel
  subscriptions.

Here's an example file:

```json
{
  "secrets": {
  "CALENDAR_ID": "f00b4r1f00b4r2f00b4r3f00b4r@group.calendar.google.com",
  "MARVEL_COOKIE": "marvel_autologin=205250250250250213023...;"
  },
  "subscriptions": [
    {
      "title": "Unbeatable Squirrel Girl",
      "shortname": "USG",
      "startFrom": "5"
    }
  ]
}
```

## TODOs

- Add option to add event to calendar for expected issue arrival dates
- Refactor code to handle a lack of config info
- ~~Use iCal instead of Google-specific calendar~~
- Add alternative output formats
- Add alternative output destinations
- Add flag to not update the status file
- Rework notification system
- Add option for notifications when subscriptions are running out
- Add help text
- Add quiet mode / make default mode less noisy
- Add setup tool / mode for creating `config.json` file

## License

MIT