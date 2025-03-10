import feedparser
import sqlite3
import os
from datetime import datetime
import sys
import smtplib
from email.mime.text import MIMEText
from dateutil import parser
from datetime import timezone, timedelta
import csv
import argparse

# Set up argument parser
argparser = argparse.ArgumentParser(description="Send new RSS feed entries via email.")
argparser.add_argument("hour_to_send", type=int, nargs='?', help="Hour of the day to check and send new feeds (0-23)")
argparser.add_argument("feed_url", type=str, nargs='?', help="URL of the RSS feed to check")
argparser.add_argument("--sql", action="store_true", help="Open an SQL prompt to query the SQLite database")
args = argparser.parse_args()

# Determine script's directory and set database path
script_dir = os.path.dirname(os.path.realpath(__file__))
db_path = os.path.join(os.path.dirname(script_dir), "data", "rss_feed.db")

# Ensure data directory exists
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Connect to the SQLite database (creates it if it doesn't exist)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS rss_entries (
    url TEXT PRIMARY KEY,
    title TEXT,
    description TEXT,
    publication_date TEXT,
    entry_date TEXT,
    inserted_at TEXT
);
''')

# If --sql argument is provided, open an SQL prompt
if args.sql:
    print("Entering SQL prompt mode. Type your SQL queries below (type 'exit' to quit).")
    while True:
        query = input("SQL> ")
        if query.lower() == 'exit':
            break
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows:
                output = csv.writer(sys.stdout)
                output.writerow([desc[0] for desc in cursor.description])  # write headers
                output.writerows(rows)
            else:
                print("No results.")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
    conn.close()
    sys.exit()

# Get the hour to check feeds from the arguments
hour_to_send = args.hour_to_send

# Get current time and hour
now = datetime.now()

# Get the last inserted_at time from the database
cursor.execute("SELECT inserted_at FROM rss_entries ORDER BY datetime(inserted_at) DESC LIMIT 1")
last_inserted = cursor.fetchone()
if last_inserted:
    last_inserted_time = datetime.fromisoformat(last_inserted[0])
    print(f"Last inserted_at time: {last_inserted_time}")
    if now.hour >= hour_to_send and (now - last_inserted_time) >= timedelta(hours=24):
        # Proceed with checking and sending new entries
        pass
    else:
        print("Not time to check new feeds.")
        sys.exit()
else:
    # No entries, proceed with the script
    pass

# RSS feed URL
feed_url = args.feed_url

# Parse the RSS feed
feed = feedparser.parse(feed_url)

# List to store new entries
new_entries = []

# Process entries in reverse order to start with the oldest
for entry in reversed(feed.entries):
    # Check if the entry is already in the database
    cursor.execute("SELECT url FROM rss_entries WHERE url = ?", (entry.link,))
    if not cursor.fetchone():
        # Insert the new entry into the database
        cursor.execute("INSERT INTO rss_entries (url, title, description, publication_date, entry_date, inserted_at) VALUES (?, ?, ?, ?, ?, ?)",
               (entry.link, entry.title, entry.summary, datetime(*entry.published_parsed[:6]).isoformat(), datetime.now().isoformat(), datetime.now().isoformat()))
        # Add the new entry to the list
        new_entries.append(entry)

# Commit changes and close the connection
conn.commit()
conn.close()

# Compile new entries into an email
if new_entries:
    email_body = ""
    for entry in new_entries:
        email_body += f"<h2><a href='{entry.link}'>{entry.title}</a></h2>"
        email_body += f"<p>{entry.summary}</p>"
        publication_date = parser.parse(entry.published)
        # Convert publication date to local time
        local_timezone = datetime.now().astimezone().tzinfo
        formatted_date = publication_date.astimezone(local_timezone).strftime("%b %d at %I%p %Z")
        email_body += f"<p>Publication Date: {formatted_date}</p>"

    # Email configuration
    sender_email = os.environ.get("FEEDSEND_SENDER_EMAIL")
    receiver_email = os.environ.get("FEEDSEND_RECEIVER_EMAIL")
    subject = os.environ.get("FEEDSEND_EMAIL_SUBJECT") or "New RSS feed entries"

    smtp_server = os.environ.get("FEEDSEND_SMTP_SERVER")
    smtp_port = int(os.environ.get("FEEDSEND_SMTP_PORT"))
    smtp_username = os.environ.get("FEEDSEND_SMTP_USERNAME")
    smtp_password = os.environ.get("FEEDSEND_SMTP_PASSWORD")

    # Create the email message
    message = MIMEText(email_body, "html")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    # Send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
    print(f"Sent email with {len(new_entries)} new feeds")

else:
    print("No new feeds")
