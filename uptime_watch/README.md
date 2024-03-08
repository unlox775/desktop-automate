# Uptime Watch

Uptime Watch is a simple Python script designed to monitor the uptime of a specified website and send an email alert if the status of the website changes (e.g., from UP to DOWN or vice versa). This script uses a SQLite database to track the status of the website over time.

## Requirements

- Python 3.x
- `requests` library for making HTTP requests.
- `smtplib` and `email` libraries for sending emails.
- Access to an SMTP server for sending email alerts.

## Setup

### Install Python Dependencies

First, ensure you have Python 3 installed on your system. Then, install the required Python libraries by running:

```bash
pip install requests
```

### Environment Variables

The script uses environment variables for email configuration. Set the following variables in your environment or script:

- `UPTIMEWATCH_SENDER_EMAIL`: The email address from which the alerts will be sent.
- `UPTIMEWATCH_RECEIVER_EMAIL`: The email address to receive the alerts.
- `UPTIMEWATCH_SMTP_SERVER`: The SMTP server address.
- `UPTIMEWATCH_SMTP_PORT`: The SMTP server port.
- `UPTIMEWATCH_SMTP_USERNAME`: The SMTP username for authentication.
- `UPTIMEWATCH_SMTP_PASSWORD`: The SMTP password for authentication.

You can set these variables in your shell environment or within a secrets file that you source before running the script.

### Database Setup

The script automatically creates a SQLite database and table for tracking website status. Ensure the script has permission to write to the database directory.

### Crontab Entry

To regularly check website uptime, add a crontab entry like the following, adjusting paths as necessary:

```bash
DESKTOP_AUTOMATE=/path/to/desktop-automate
LOG=/path/to/desktop-automate/data/cron.log
SECRETS=/path/to/personal.secrets.sh
DA_PYTHON=/path/to/desktop-automate/venv/bin/python3
UPTIME=/path/to/desktop-automate/uptime_watch/check_url_uptime.py


0/5 * * * * . $SECRETS ; $DA_PYTHON $UPTIME https://site-one.org/ 2>&1 >> $LOG
0/5 * * * * . $SECRETS ; $DA_PYTHON $UPTIME https://site-two.com/ 2>&1 >> $LOG
```

Replace `<URL>` with the website URL you wish to monitor.

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

To manually check a website's uptime and send an alert if the status has changed, run:

```bash
python3 check_url_uptime.py <URL>
```

Replace `<URL>` with the website URL you wish to monitor.
