# RSS Feed Notifier README

## Overview
This RSS Feed Notifier script provides a simple, free alternative to services like MailBrew. It automatically fetches new entries from a specified RSS feed and sends them to your email. The script is designed to run on a macOS system and stores feed entries in a local SQLite database to avoid sending duplicate notifications.

## Features
- **RSS Feed Parsing**: Automatically retrieves new entries from the specified RSS feed URL.
- **SQLite Database Storage**: Stores feed entries locally to track already notified entries.
- **Email Notifications**: Sends an email with new feed entries since the last run.
- **Environment Variables for Configuration**: Uses environment variables for email configuration, making it easy to customize sender, receiver, and SMTP settings.

## Requirements
- Python 3
- `feedparser` Python package
- Access to an SMTP server (Gmail SMTP recommended)
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

4. **Configure environment variables** for email settings. You can set these in your `.bashrc`, `.zshrc`, or `.profile`, or prefix them before running the script:

    ```
    export FEEDSEND_SENDER_EMAIL='your_email@example.com'
    export FEEDSEND_RECEIVER_EMAIL='recipient_email@example.com'
    export FEEDSEND_EMAIL_SUBJECT='New RSS Feed Entries'
    export FEEDSEND_SMTP_SERVER='smtp.example.com'
    export FEEDSEND_SMTP_PORT='587'
    export FEEDSEND_SMTP_USERNAME='your_username'
    export FEEDSEND_SMTP_PASSWORD='your_password'
    ```

    Replace placeholder values with your actual email configuration.

### How to set up GMail App Passwords (Recommended if 2-Step Verification is Enabled):

Instructions courtesy of ChatGPT:

1. **Enable 2-Step Verification**:
   - Visit your Google Account's security settings at [Google Account Security](https://myaccount.google.com/security).
   - Scroll down to the "Signing in to Google" section and select "2-Step Verification."
   - Follow the prompts to set up 2-Step Verification.

2. **Create an App Password**:
   - Once 2-Step Verification is enabled, return to the [Google Account Security](https://myaccount.google.com/security) page.
   - Scroll to the "Signing in to Google" section again and click on "App passwords."
   - You may be prompted to sign in again.
   - Select the app and device you want to generate the password for. For your case, you might choose "Mail" as the app and "Mac" as the device.
   - Click "Generate." Google will display a 16-character password.
   - Use this app password in your script as the `smtp_password`.

## Usage

Run the script from the command line, specifying the RSS feed URL as an argument:

```
python3 send_new_feeds_email.py 'http://example.com/feed'
```

## Cron Job Setup

To run this script automatically at regular intervals, you can set up a cron job on macOS:

1. **Open Terminal**.
2. **Edit your crontab**:

    ```
    crontab -e
    ```

3. **Add a cron job** to run the script hourly (modify the schedule as needed):

    ```
    0 * * * * /path/to/your/python3 /path/to/send_new_feeds_email.py 'http://example.com/feed' 2>&1 | awk '{ print strftime("[%Y-%m-%d %H:%M:%S]"), $0; fflush(); }' >> /path/to/logfile.log
    ```

    Make sure to replace `/path/to/your/python` and `/path/to/send_new_feeds_email.py` with the actual paths on your system.

## Notes

- The first time you run the script, it will send notifications for all current entries in the feed. Subsequent runs will only notify you about new entries.
- Ensure your SMTP settings are correctly configured to prevent email sending errors.
- For Gmail SMTP, you may need to create an App Password if you have 2-Step Verification enabled on your Google account (see above).
- If you use for more than one feed, technically it will skip sending a feed entry from one feed if it's already in the database from another feed. This is because the script uses the entry's URL as a unique identifier. If you want to use this for multiple feeds, you may want to modify the database schema to include the feed URL as part of the unique identifier.