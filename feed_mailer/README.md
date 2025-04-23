# RSS Feed Mailer

## Overview
This RSS Feed Mailer script provides a simple, free alternative to services like MailBrew. It automatically fetches new entries from a specified RSS feed and sends them to your email. The script stores feed entries in a local SQLite database to avoid sending duplicate notifications.

## Features
- **RSS Feed Parsing**: Automatically retrieves new entries from the specified RSS feed URL.
- **SQLite Database Storage**: Stores feed entries locally to track already notified entries.
- **Email Notifications**: Sends an email with new feed entries since the last run.
- **Command Line Interface**: Includes commands for checking feeds, querying the database, and listing recent entries.
- **Environment Variables for Configuration**: Uses environment variables for email configuration, making it easy to customize.
- **Customizable Database Path**: Store your feed database wherever you want.

## Requirements
- Python 3
- `feedparser` Python package
- `python-dateutil` package
- Access to an SMTP server
- SQLite3 (Included with Python)

## Installation

1. **Clone the repository or download the script** to your local machine.
2. **Set up a virtual environment** (optional but recommended):

    ```
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install dependencies**:

    ```
    pip3 install feedparser python-dateutil
    ```

4. **Configure environment variables** for email settings:

    ```
    export FEEDSEND_SENDER_EMAIL='your_email@example.com'
    export FEEDSEND_RECEIVER_EMAIL='recipient_email@example.com'
    export FEEDSEND_EMAIL_SUBJECT='New RSS Feed Entries'
    export FEEDSEND_SMTP_SERVER='smtp.example.com'
    export FEEDSEND_SMTP_PORT='587'
    export FEEDSEND_SMTP_USERNAME='your_username'
    export FEEDSEND_SMTP_PASSWORD='your_password'
    ```

    You can also set `FEEDSEND_DB_PATH` to override the default database location.

### How to set up GMail App Passwords (If using Gmail with 2-Step Verification):

1. **Enable 2-Step Verification**:
   - Visit your Google Account's security settings at [Google Account Security](https://myaccount.google.com/security).
   - Scroll down to the "Signing in to Google" section and select "2-Step Verification."
   - Follow the prompts to set up 2-Step Verification.

2. **Create an App Password**:
   - Once 2-Step Verification is enabled, return to the [Google Account Security](https://myaccount.google.com/security) page.
   - Scroll to the "Signing in to Google" section again and click on "App passwords."
   - You may be prompted to sign in again.
   - Select "Mail" as the app and your device type.
   - Click "Generate." Google will display a 16-character password.
   - Use this app password in your script as the `FEEDSEND_SMTP_PASSWORD`.

## Usage

### Command Line Interface

The script provides a command-line interface with several commands:

#### Check for new feed entries

```
python3 send_new_feeds_email.py check --feed 'https://example.com/feed'
```

Optional arguments:
- `--hour HOUR`: Hour of the day to check feeds (default: 9 or `FEEDSEND_HOUR` env variable)
- `--force`: Force sending even if time conditions aren't met
- `--db-path PATH`: Custom path to the SQLite database
- `--verbose` or `-v`: Show verbose output

#### Query the database with SQL

```
python3 send_new_feeds_email.py sql
```

Optional arguments:
- `--db-path PATH`: Custom path to the SQLite database

#### List recent entries

```
python3 send_new_feeds_email.py list
```

Optional arguments:
- `--limit N`: Number of entries to show (default: 10)
- `--db-path PATH`: Custom path to the SQLite database

### Cron Job Setup

To run this script automatically at regular intervals using the provided wrapper script:

1. Configure cron to run the script at the desired time:

    ```
    # Email every morning at 9am
    0 9 * * * /path/to/desktop-automate/cron_run_w_log.sh /path/to/desktop-automate/feed_mailer/send_new_feeds_email.py check --feed https://example.com/feed
    ```

Alternatively, you can set environment variables in your crontab:

```
FEEDSEND_SENDER_EMAIL=your_email@example.com
FEEDSEND_RECEIVER_EMAIL=recipient_email@example.com
# ...other environment variables...

0 9 * * * cd /path/to/desktop-automate && ./venv/bin/python feed_mailer/send_new_feeds_email.py check --feed https://example.com/feed
```

## Notes

- The first time you run the script, it will send notifications for all current entries in the feed. Subsequent runs will only notify you about new entries.
- Ensure your SMTP settings are correctly configured to prevent email sending errors.
- If you use this for multiple feeds, you might want to set up separate database files for each feed by using the `--db-path` option.
- The script uses the entry's URL as the unique identifier in the database.