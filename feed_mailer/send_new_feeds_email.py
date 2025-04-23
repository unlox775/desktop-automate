#!/usr/bin/env python3
"""
RSS Feed Mailer - A tool for monitoring RSS feeds and sending new entries via email.

This script checks an RSS feed for new entries and emails them to a specified address.
It stores the entries in a SQLite database to track what has already been sent.

Configuration is via command-line arguments and environment variables.
"""
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
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("feed_mailer")

def setup_argparser():
    """Configure and return the argument parser for the script."""
    argparser = argparse.ArgumentParser(
        description="Send new RSS feed entries via email or manage the feed database.",
        epilog="Environment variables FEEDSEND_* can be used for email configuration."
    )
    
    # Create a subparser for different commands
    subparsers = argparser.add_subparsers(dest="command", help="Command to execute")
    
    # Check command for checking and sending new feeds
    check_parser = subparsers.add_parser("check", help="Check for new feed entries and email them")
    check_parser.add_argument("--hour", type=int, help="Hour of the day to check and send new feeds (0-23)", default=int(os.environ.get("FEEDSEND_HOUR", "9")))
    check_parser.add_argument("--feed", type=str, help="URL of the RSS feed to check", required=True)
    check_parser.add_argument("--force", action="store_true", help="Force sending even if time conditions aren't met")
    check_parser.add_argument("--db-path", type=str, help="Path to the SQLite database", default=None)
    check_parser.add_argument("--verbose", "-v", action="store_true", help="Show verbose output")
    
    # SQL command for querying the database
    sql_parser = subparsers.add_parser("sql", help="Open an SQL prompt to query the feed database")
    sql_parser.add_argument("--db-path", type=str, help="Path to the SQLite database", default=None)
    
    # List command for showing recent entries
    list_parser = subparsers.add_parser("list", help="List recent entries in the feed database")
    list_parser.add_argument("--limit", type=int, help="Number of entries to show", default=10)
    list_parser.add_argument("--db-path", type=str, help="Path to the SQLite database", default=None)
    
    return argparser

def get_db_path(cli_path=None):
    """Determine the database path based on CLI argument or default location."""
    if cli_path:
        return os.path.abspath(cli_path)
    
    # Environment variable override
    if os.environ.get("FEEDSEND_DB_PATH"):
        return os.environ.get("FEEDSEND_DB_PATH")
    
    # Default location relative to script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(os.path.dirname(script_dir), "data", "rss_feed.db")

def setup_database(db_path):
    """Set up database connection and create tables if needed."""
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
    
    return conn, cursor

def run_sql_prompt(db_path):
    """Run an interactive SQL prompt for the database."""
    conn, cursor = setup_database(db_path)
    
    print(f"Entering SQL prompt mode for database: {db_path}")
    print("Type your SQL queries below (type 'exit' to quit).")
    
    while True:
        try:
            query = input("SQL> ")
            if query.lower() in ("exit", "quit", ".exit", ".quit", "\\q"):
                break
                
            cursor.execute(query)
            rows = cursor.fetchall()
            
            if cursor.description:  # Check if the query returned any columns
                if rows:
                    output = csv.writer(sys.stdout)
                    output.writerow([desc[0] for desc in cursor.description])  # write headers
                    output.writerows(rows)
                else:
                    print("Query returned no rows.")
            else:
                print(f"Query executed successfully. Rows affected: {cursor.rowcount}")
                
        except sqlite3.Error as e:
            print(f"SQL error: {e}")
        except KeyboardInterrupt:
            print("\nExiting SQL prompt...")
            break
        except Exception as e:
            print(f"Error: {e}")
    
    conn.close()

def list_recent_entries(db_path, limit):
    """List recent entries from the database."""
    conn, cursor = setup_database(db_path)
    
    try:
        cursor.execute("""
            SELECT title, publication_date, url 
            FROM rss_entries 
            ORDER BY datetime(inserted_at) DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        
        if rows:
            print(f"Recent {limit} entries:")
            for i, (title, pub_date, url) in enumerate(rows, 1):
                print(f"{i}. {title} ({pub_date})")
                print(f"   {url}")
                print()
        else:
            print("No entries found in the database.")
    finally:
        conn.close()

def check_and_send_feeds(db_path, feed_url, hour_to_send, force=False, verbose=False):
    """Check for new feed entries and email them."""
    conn, cursor = setup_database(db_path)
    
    if verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        # Get current time
        now = datetime.now()
        logger.debug(f"Current time: {now}")
        
        # Check timing conditions unless forced
        if not force:
            # Get the last inserted_at time from the database
            cursor.execute("SELECT inserted_at FROM rss_entries ORDER BY datetime(inserted_at) DESC LIMIT 1")
            last_inserted = cursor.fetchone()
            
            if last_inserted:
                last_inserted_time = datetime.fromisoformat(last_inserted[0])
                logger.debug(f"Last inserted_at time: {last_inserted_time}")
                
                if not (now.hour >= hour_to_send and (now - last_inserted_time) >= timedelta(hours=24)):
                    logger.info("Not time to check new feeds. Use --force to override.")
                    return
        
        # Parse the RSS feed
        logger.info(f"Checking feed: {feed_url}")
        feed = feedparser.parse(feed_url)
        
        if hasattr(feed, 'status') and feed.status != 200:
            logger.error(f"Error fetching feed. Status code: {feed.status}")
            if hasattr(feed, 'bozo_exception'):
                logger.error(f"Exception: {feed.bozo_exception}")
            return
        
        # List to store new entries
        new_entries = []
        entries_to_insert = []
        
        # Process entries in reverse order to start with the oldest
        for entry in reversed(feed.entries):
            # Check if the entry is already in the database
            cursor.execute("SELECT url FROM rss_entries WHERE url = ?", (entry.link,))
            if not cursor.fetchone():
                # Store the entry data to be inserted later
                entries_to_insert.append((
                    entry.link, 
                    entry.title, 
                    entry.summary, 
                    datetime(*entry.published_parsed[:6]).isoformat(), 
                    datetime.now().isoformat(), 
                    datetime.now().isoformat()
                ))
                # Add the new entry to the list
                new_entries.append(entry)
        
        # Send email if there are new entries
        if new_entries:
            email_success = send_entries_email(new_entries)
            
            # Only commit changes to database if email was sent successfully
            if email_success:
                # Insert all entries into the database
                for entry_data in entries_to_insert:
                    cursor.execute(
                        """INSERT INTO rss_entries 
                           (url, title, description, publication_date, entry_date, inserted_at) 
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        entry_data
                    )
                # Commit changes to database
                conn.commit()
                logger.info(f"Committed {len(new_entries)} new entries to database")
            else:
                logger.warning("Email sending failed, not committing entries to database")
        else:
            logger.info("No new feed entries found.")
        
    finally:
        conn.close()

def send_entries_email(entries):
    """Send an email with the new feed entries."""
    # Email configuration from environment variables
    sender_email = os.environ.get("FEEDSEND_SENDER_EMAIL")
    receiver_email = os.environ.get("FEEDSEND_RECEIVER_EMAIL")
    subject = os.environ.get("FEEDSEND_EMAIL_SUBJECT", "New RSS feed entries")
    
    smtp_server = os.environ.get("FEEDSEND_SMTP_SERVER")
    smtp_port = int(os.environ.get("FEEDSEND_SMTP_PORT", "587"))
    smtp_username = os.environ.get("FEEDSEND_SMTP_USERNAME")
    smtp_password = os.environ.get("FEEDSEND_SMTP_PASSWORD")
    
    # Check if email configuration is complete
    if not all([sender_email, receiver_email, smtp_server, smtp_username, smtp_password]):
        logger.error("Email configuration incomplete. Please set all FEEDSEND_* environment variables.")
        logger.info(f"Found {len(entries)} new entries, but email was not sent due to missing configuration.")
        return False
    
    # Compile new entries into an email
    email_body = ""
    for entry in entries:
        email_body += f"<h2><a href='{entry.link}'>{entry.title}</a></h2>"
        email_body += f"<p>{entry.summary}</p>"
        publication_date = parser.parse(entry.published)
        # Convert publication date to local time
        local_timezone = datetime.now().astimezone().tzinfo
        formatted_date = publication_date.astimezone(local_timezone).strftime("%b %d at %I%p %Z")
        email_body += f"<p>Publication Date: {formatted_date}</p>"
        email_body += "<hr>"
    
    # Create the email message
    message = MIMEText(email_body, "html")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email
    
    # Send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        logger.info(f"Sent email with {len(entries)} new feed entries")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

def main():
    """Main entry point for the script."""
    argparser = setup_argparser()
    args = argparser.parse_args()
    
    # Determine database path
    db_path = get_db_path(getattr(args, "db_path", None))
    
    if args.command == "sql":
        run_sql_prompt(db_path)
    elif args.command == "list":
        list_recent_entries(db_path, args.limit)
    elif args.command == "check":
        check_and_send_feeds(db_path, args.feed, args.hour, args.force, args.verbose)
    else:
        # If no command is provided, show help
        argparser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
