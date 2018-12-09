# MarvelMailer

![MarvelMailer Logo](icon/icon_big.png)

*Tracks Marvel subscriptions by keeping an eye on issue processing and shipping*

## Overview

Marvel Mailer is a tool designed to automatically track Marvel mail order 
subscriptions by scraping the 
['My Account' page](https://subscriptions.marvel.com/accounts/myaccount.asp),
and adding events to a calendar when a new issue is processed or shipped.

This is done by storing a record of each subscription's status, which is
compared with the current status on the webpage. If a difference is detected,
events are dispatched for the status changes.

## Setup

### Requirements

- Python 3.5+
- Various Python packages. See `requirements.txt` for package list.

### Steps

1. Create a OAuth Client ID secret file for accessing your Google Account. 
   For more details instructions, see 
   [Google's sample instructions](https://developers.google.com/api-client-library/python/samples/samples).
    1. Visit [Developer Dashboard](https://console.developers.google.com/apis/credentials)
       and create a project.
    2. [Enable "Calendar API" for the project](https://console.developers.google.com/apis/library/calendar-json.googleapis.com/). 
    3. [Add OAuth to the project](https://console.developers.google.com/apis/credentials/oauthclient).
    4. [Download the JSON secrets file](https://console.developers.google.com/apis/credentials).
2. Retrieve your calendar ID
    1. Visit the [settings page](https://calendar.google.com/calendar/r) for 
       the calendar you wish to use.
    2. Grab the calendar ID from the URL. It will look something like: 
       `https://calendar.google.com/calendar/r/settings/calendar/<CalendarIDHere>?pli=1`
3. Retrieve your [Marvel Subscription](https://subscriptions.marvel.com/accounts/myaccount.asp)
    login cookie. The name or key should be `marvel_autologin`. Exact 
    instruction for retrieving cookies will depend on your browser. See 
   [WikiHow for more information](https://www.wikihow.com/View-Cookies).
4. Add these secrets to your `config.json` file. See 'Config File Format' for 
   more details.
5. Add details for each comic subscription to your `config.json`, by adding a
   title, short name and issue number from which the subscription starts.

## Usage

Run `python marvelMailer.py`

```bash
$ python marvelMailer.py --help
usage: marvelMailer.py [-h] [--version] [-q | -s] [config_file]

positional arguments:
  config_file   config file, in JSON format

optional arguments:
  -h, --help    show this help message and exit
  --version     print version
  -q, --quiet   quiet output
  -s, --silent  silent output
...
```

### First Run

On first run, you must authorise the application to access your Google account 
and calendar. This is done by running the application, which will prompt you 
with a URL to visit, where you will need to login to a Google Account with 
access to the calendar you want to use, authorise access to the calendar, and 
copy a code to pass back to the application.

For more technical details, see 
[this article by Google](https://developers.google.com/api-client-library/python/auth/installed-app).

## Config File Format

A config file is required to specify various necessary operational information. 
It should match the following basic structure:

```json
{
  "secrets": {
    "marvel_cookie": "<cookie keys>",
    "calendar_id": "<calendar id>",
    "client_secret_file": "<client secret filename>"
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
  },
  "subscription_file": "<subscription status filename>",
  "expected_delivery_time": "<expected delivery days>"
}
```
### Secrets
This section is where all secret information used to perform authentication and
event handling is specified.
- `marvel_cookie` is your authorization cookie for accessing the
  [Marvel 'My Accounts' page](https://subscriptions.marvel.com/accounts/myaccount.asp).
- `calendar_id` is the unique ID of the calendar you want to add events to.
- `client_secret_file` is the filename of the JSON file containing the Google API
  OAuth credentials tokens, used to access the Google Calendar API. 
   
### Subscriptions
This section is where the details of each Marvel subscription are 
specified.
- `title` is the title of the comic series, as it appears on the 'My Accounts' 
  page. 
- `short_name` is a user-chosen alternative name for the comic series. This is 
  used in event titles to reduce the bulk of using full titles.
- `start_from` is the issue number of the first issue you received through
  Marvel subscriptions.
   
### Notifier
This section allows you to specify how to notify you of warnings and errors. 
This section is ***optional***, and the console will be used if it is not 
specified.  
- `method` specifies the method through which notifications and errors should be
  sent. Currently, two options are supported: 
  + `console` which uses `stdout/stderr`. This is the default behaviour.
  + `telegram` which uses a user-created bot to send messages through the 
    Telegram Messenger API.

 If you has elected to use `telegram`, the following fields must also be 
 specified. More information on how to obtain these details can be found 
 [in this article](https://www.forsomedefinition.com/automation/creating-telegram-bot-notifications/).
 - `bot_token` is the secret token used by the Telegram bot.
 - `user_id` is the Telegram ID that should be sent notifications.
 
### Other
 - `subscription_file` is the filename of the JSON file to be used as the 
   subscription file, where subscriptions' statuses are stored. This field is 
   ***optional***. If not specified, the subscription file will be stored in 
   the OS-specific user data directory. 
 - `expected_delivery_time` is the number of days that a comic usually takes to 
   be delivered after it is marked as shipped on the Marvel 'My Accounts' page.
   This field is ***optional***. If specified, an additional event will be added 
   to the specified calendar when an issue is shipped, to signify when the issue
   is expected to arrive. Otherwise, this functionality is disabled. 

Here's an example file:

```json
{
  "secrets": {
    "marvel_cookie": "marvel_autologin=205250250250250213023...;",
    "calendar_id": "f00b4r1f00b4r2f00b4r3f00b4r@group.calendar.google.com",
    "client_secret_file": "data/client_id.json"
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
  },
  "subscription_file": "data/issueStatus.json",
  "expected_delivery_time": 14
}
```

## TODOs

- Add option to add event to calendar for expected issue arrival dates
- Scrape inactive subscriptions to make sure we get the last issue 
- Add alternative output formats
- Add alternative output destinations
- Add option to not update the status file
- Add option for notifications when subscriptions are running out
- Add notifications for all errors
- Handle expired calendar authorisation notification/renewal

## License

MIT