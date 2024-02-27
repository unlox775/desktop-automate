import os
import sqlite3
import requests
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import sys

# Determine the script's directory and set the database path
script_dir = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(os.path.dirname(script_dir), "data", "uptime_watch.db")

# Ensure the data directory exists
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Connect to the SQLite database (creates it if it doesn't exist)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS website_status (
    url TEXT PRIMARY KEY,
    status TEXT,
    last_checked TEXT
);
''')

# Website URL to check
# Read the URL from the first command line argument
website_url = sys.argv[1]

# Function to send email
def send_email(subject, body):
    sender_email = os.environ.get("UPTIMEWATCH_SENDER_EMAIL")
    receiver_email = os.environ.get("UPTIMEWATCH_RECEIVER_EMAIL")
    smtp_server = os.environ.get("UPTIMEWATCH_SMTP_SERVER")
    smtp_port = int(os.environ.get("UPTIMEWATCH_SMTP_PORT"))
    smtp_username = os.environ.get("UPTIMEWATCH_SMTP_USERNAME")
    smtp_password = os.environ.get("UPTIMEWATCH_SMTP_PASSWORD")

    message = MIMEText(body, "plain")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, receiver_email, message.as_string())

# Function to check website status
def check_website(url):
    try:
        response = requests.get(url, timeout=10)
        return 'UP' if response.status_code == 200 else 'DOWN'
    except requests.RequestException:
        return 'DOWN'

# Check the current status of the website
current_status = check_website(website_url)

# Fetch the last status from the database
cursor.execute("SELECT status FROM website_status WHERE url = ?", (website_url,))
row = cursor.fetchone()
last_status = row[0] if row else None

# If the status has changed, update the database and send an email
if current_status != last_status:
    cursor.execute("REPLACE INTO website_status (url, status, last_checked) VALUES (?, ?, ?)",
                   (website_url, current_status, datetime.now().isoformat()))
    conn.commit()

    subject = f"Uptime Watch Alert: {website_url} is now {current_status}"
    body = f"The status of {website_url} has changed to {current_status}."
    send_email(subject, body)

# Commit changes and close the connection
conn.commit()
conn.close()

print(f"Checked {website_url}, status: {current_status}")
