import smtplib
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

# read from environment variables
drama_roll_link = os.environ.get("DRAMA_ROLL_LINK")
drama_attendance_gsheet = os.environ.get("DRAMA_ATTENDANCE_GSHEET")
drama_receiver_emails = os.environ.get("DRAMA_RECEIVER_EMAILS").split(" ")

# Load and parse the given URL
def load_and_parse_url(url):
    session = requests.Session()
    response = session.get(url)

    # Follow redirects if there is a 302 found response
    if response.status_code == 302:
        redirect_url = response.headers['Location']
        response = session.get(redirect_url)

    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

# Extract data from the table and check if today's date is in the table
def extract_attendance_data(soup):
    today = datetime.now().strftime('%d %b')
    # print("Today:", today)
    
    # Find the table and parse rows
    table = soup.find('table', {'class': 'waffle'})
    rows = table.find_all('tr')[3:]  # Skip header row and the first row with no data
    
    attendance_data = []
    for row in rows:
        columns = row.find_all('td')
        date = columns[0].get_text().strip()
        # print(date)
        if today in date:
            attendance_data.append({
                'date': date,
                'first_hour': columns[3].get_text().strip().replace(', ', '\n- '),
                'whole_time': columns[4].get_text().strip().replace(', ', '\n- '),
                'last_hour': columns[5].get_text().strip().replace(', ', '\n- '),
                'other': columns[6].get_text().strip().replace(', ', '\n- ')
            })
    
    return attendance_data

# Format email body
def format_email_content(attendance_data):
    today = datetime.now().strftime('%d %b %Y')

    if not attendance_data:
        return f"Subject: {today} - Excused Absences Report\n\n" \
               "No one is planned to be absent on this day."

    content = f"Subject: {today} - Excused Absences Report\n\n" \
              "The following have registered an excused absence for today:\n\n"
    
    for entry in attendance_data:
        if entry['first_hour']:
            content += f"Absent during the 1st hour:\n- {entry['first_hour']}\n\n"
        if entry['whole_time']:
            content += f"Absent the whole time:\n- {entry['whole_time']}\n\n"
        if entry['last_hour']:
            content += f"Absent during the last hour:\n- {entry['last_hour']}\n\n"
        if entry['other']:
            content += f"Absent for other times:\n- {entry['other']}\n\n"
    
    # Add the handy link to take roll at the end
    content += "Handy Link to take Roll today: " + drama_roll_link
    
    return content

# Main function to load the URL, parse the data, and generate email content
def main():
    url = drama_attendance_gsheet
    soup = load_and_parse_url(url)
    attendance_data = extract_attendance_data(soup)
    if not attendance_data:
        print("No rehearsal today.")
        return
    
    email_body = format_email_content(attendance_data)

    # Email configuration
    sender_email = os.environ.get("FEEDSEND_SENDER_EMAIL")
    receiver_emails = drama_receiver_emails
    today = datetime.now().strftime('%d %b %Y')
    subject = f"Excused Absences Report for {today}"

    smtp_server = os.environ.get("FEEDSEND_SMTP_SERVER")
    smtp_port = int(os.environ.get("FEEDSEND_SMTP_PORT"))
    smtp_username = os.environ.get("FEEDSEND_SMTP_USERNAME")
    smtp_password = os.environ.get("FEEDSEND_SMTP_PASSWORD")

    # Create the email message
    for receiver_email in receiver_emails:
        message = MIMEText(email_body, "plain")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = receiver_email

        # Send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print(f"Sent email for {today} to {receiver_email}")

if __name__ == "__main__":
    main()