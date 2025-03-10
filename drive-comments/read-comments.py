from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import re
import sys

# Path to the OAuth 2.0 Client ID JSON file
CLIENT_SECRETS_FILE = '../credentials.json'  # Update this with the correct path

# Scopes required for the Drive API
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_credentials():
    # Perform the OAuth 2.0 authorization flow
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    return credentials

def list_comments(file_id, service):
    """List comments on a Google Drive file."""
    results = service.comments().list(
        fileId=file_id,
        fields="comments"
    ).execute()
    comments = results.get('comments', [])
    for comment in comments:
        print(f'Comment: {comment["content"]}, Author: {comment["author"]["displayName"]}')

def extract_id_from_url(url):
    """Extract the Google Drive file ID from a URL."""
    match = re.search(r'/d/(.*?)/', url)
    if match:
        return match.group(1)
    else:
        return url

if __name__ == '__main__':
    # Authenticate and construct service
    credentials = get_credentials()
    service = build('drive', 'v3', credentials=credentials)

    # Get the file ID or URL from the command line
    input = sys.argv[1]
    file_id = extract_id_from_url(input)
    list_comments(file_id, service)