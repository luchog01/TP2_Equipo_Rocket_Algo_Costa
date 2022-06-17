import os

from io import TextIOWrapper
from urllib import response
from googleapiclient.discovery import Resource, build
from googleapiclient.errors import HttpError, Error
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from requests import request
import httplib2

# UCd_QeeJYwLmb13KUP0E3FHw channel id
# Primera Playlist PLIG13vm2QTYwCFv8lDl0SOiq1Tjwie_Ko

SCOPES = [
    'https://www.googleapis.com/auth/youtube'
]

# Archivo generado para la API
ARCHIVO_SECRET_CLIENT = 'credentials.json'
ARCHIVO_TOKEN = 'token.json'

def login() -> Resource:
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(ARCHIVO_TOKEN):
        creds = Credentials.from_authorized_user_file(ARCHIVO_TOKEN, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                ARCHIVO_SECRET_CLIENT, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(ARCHIVO_TOKEN, 'w') as token:
            token.write(creds.to_json())

 
    return build("youtube", "v3", credentials=creds)
  
   