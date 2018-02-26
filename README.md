# MarvelMailer

*Tracks Marvel subscriptions by keeping an eye on issue processing and shipping*

## Overview

Marvel Mailer is a tool designed to automatically track Marvel mail order 
subscriptions by scraping the 
['My Account' page](https://subscriptions.marvel.com/accounts/myaccount.asp),
and adding events to a calendar when a new issue is processed or shipped.

This is done by storing a record of each subscription's status, which is
compared with the current status on the webpage. If a difference is detected,
events are dispatched for these status changes.

## Setup

### Requirements

- Python 3.6+
- Various python packages. See `requirements.txt` for package list.

### Steps

1. Create a `client_id` secret for accessing your Google Account. 
   For more details instructions, see 
   [Google's sample instructions](https://developers.google.com/api-client-library/python/samples/samples).
    - Visit [Developer Dashboard](https://console.developers.google.com/apis/credentials)
      and create a project.
    - [Enable "Calendar API" for the project](https://support.google.com/cloud/answer/6158841). 
    - [Add OAuth to the project](https://support.google.com/cloud/answer/6158841).
    - Download `client_id.json` secret file.
2. Retrieve your calendar ID and Marvel Subscription cookie keys.
    - Visit [your calendar settings](https://calendar.google.com/calendar/r) 
      and grab the URL.
    - Visit the [Marvel Accoutns page](https://subscriptions.marvel.com/accounts/myaccount.asp)
      and use the developer panel to view the `marvel_autologin` cookie header.
3. Add these to `config.json` file. See 'Config File Format' for more details.
4. Define each comic subscription in `config.json`, by adding a title, short 
   name and issue number from which the subscription starts.

## Usage

Run `python marvelMailer.py`

```bash
$ python marvelMailer.py --help
Marvel Mailer v1
...
```

## Config File Format

A config file is required to specify various necessary operation information. 
It should match the following basic structure:

```json
{
  "secrets": {
    "marvel_cookie": "<cookie keys>",
    "calendar_id": "<calendar id>",
    "client_secret": "<client secret file>"
  },
  "subscriptions": [
    {
      "title": "<comic series title>",
      "short_name": "<series short name>",
      "start_from": "<issue number of first received issue>"
    }
  ],
  "notifier": {
    "method": "<notification method>",
    "bot_token": "<telegram bot token>",
    "user_id": "<telegram user id>"
  }
}
```

- `marvel_cookie` is your authorization cookie, taken from the `COOKIE` header 
   request to the 'My Accounts' page.
- `calendar_id` is the unique ID of the calendar you want to add events to.
- `client_secret` is the filename of the `client_id.json` file used to 
   access the Google Calendar API. 
   
- `title` is the title of the comic series, as it appears on the 'My Accounts' 
   page. 
- `short_name` is a user-chosen alternative name for the comic series. This is 
   used in event titles to reduce the bulk of using full titles.
- `start_from` is the issue number of the first issue you received through the 
   Marvel subscriptions.
   
- `method` specifies the method through with notifications and errors should be
   sent. Currently, two options are supported: `console` which uses 
   `stdout/stderr`; and `telegram` which uses a user-created bot to send 
   messages to the user through the Telegram Messenger API.
 - `bot_token` is the secret token used by the Telegram bot.
 - `user_id` is the Telegram ID of the user that should be sent notifications.    

Here's an example file:

```json
{
  "secrets": {
    "marvel_cookie": "marvel_autologin=205250250250250213023...;",
    "calendar_id": "f00b4r1f00b4r2f00b4r3f00b4r@group.calendar.google.com",
    "client_secret": "client_id.json"
  },
  "subscriptions": [
    {
      "title": "Unbeatable Squirrel Girl",
      "short_name": "USG",
      "start_from": "5"
    }
  ],
  "notifier": {
    "method": "telegram",
    "bot_token": "999999999:ABC-98pb7hN987yh8nuNYpiugyhgiyo9",
    "user_id": "555555555"
  }
}
```

## TODOs

- Add option to add event to calendar for expected issue arrival dates
- ~~Refactor code to handle a lack of config info~~
- ~~Use iCal instead of Google-specific calendar~~
- Add alternative output formats
- Add alternative output destinations
- Add flag to not update the status file
- _Rework notification system_
- Add option for notifications when subscriptions are running out
- Add help text
- _Add quiet mode / make default mode less noisy_
- Add setup tool / mode for creating `config.json` file
- Scrape inactive subscriptions to make sure we get the last issue 

## License

MIT