# README_MarvelMailer
*Tracks Marvel subscriptions by keeping an eye on issue processing and shipping*

## Overview
Marvel Mailer is a tool designed to automatically track Marvel subscriptions by scraping the Account page, and adding events to a calendar when a new issue is processed or shipped.

This is done by storing a record of issue status, which is compared with the current issue status on the webpage. If a difference is detected, events are dispatched for these status changes.

## Setup

### Requirements
- Python 3.6+
- Various python packages...
See `requirements.txt` for package list

### Steps
1. Retrieve your calendar ID and Marvel Subscription cookie keys.
2. Add these to the `secret.json` file. See 'Secret File Format' for more details.
3. Define a shortname and start at issue number for each comic subscription in the Config file. See 'Config File Format' for more details.

## Usage
Run `python marvelMailer.py`

```bash
$ python marvelMailer.py
Marvel Mailer v1
```


## Secret File Format
Secret file should follow the following basic structure:
```json
{
  "MARVEL_COOKIE": "<cookie keys>",
  "CALENDAR_ID": "<calendar id>"
}
```

## Config File Format
Config files should follow the following basic structure:
```json
[
  {
    "title": "<comic title>",
    "shortname": "<comic shortname>",
    "startAt": "<issue number before first sub>"
]
```

- Shortname is a user-chosen alternative name for the comic series. This is used in event titles to reduce the bulk of using full titles.
- startAt is the issue number of the issue before the first issue received through the subscription.

## TODOs
- Add option to add event to calendar for expected issue arrival dates
- Refactor code to handle a lack of config info
- Use iCal instead of Google-specifc calendar
- Add alternative output formats
- Add alternative output destinations
- Add flag to not update the status file
- Rework notification system
- Add option for notifications when subscriptions are running out
- Add help text
- Add quiet mode / make default mode less noisy

## License
MIT