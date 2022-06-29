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

CHANNEL_ID = 'UCd_QeeJYwLmb13KUP0E3FHw'
# Primera Playlist PLIG13vm2QTYwCFv8lDl0SOiq1Tjwie_Ko

SCOPES = [
    'https://www.googleapis.com/auth/youtube'
]

# Archivo generado para la API
FILE_SECRET_CLIENT = 'credentials.json'
FILE_TOKEN = 'token.json'

def clear() -> None:
    '''
    Clear the console for your operating system
    '''
    #Windows
    if os.name == 'nt':
        os.system('cls')
    #Linux/Mac
    else:
        os.system('clear')


def login() -> Resource:
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(FILE_TOKEN):
        creds = Credentials.from_authorized_user_file(FILE_TOKEN, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                FILE_SECRET_CLIENT, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(FILE_TOKEN, 'w') as token:
            token.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)


def new_playlist(conn: Resource) -> None:

    """
    Create a new playlist in youtube asking for its name, description and privacy status
    """

    clear()

    check1: bool = True
    while check1:
        playlist_name :str = input('Input a name for your new playlist [Max 150 char]: ')
        if len(playlist_name) <= 150:
            check1 = False
        else:
            print('Playlist name must be less than 150 characters')

    check2: bool = True
    while check2:
        playlist_description :str = input('Input a description for your new playlist [Max 5000 char]: ')
        if len(playlist_name) <= 5000:
            check2 = False
        else:
            print('Playlist description must be less than 5000 characters')

    check3: bool = True
    while check3:
        privacy: str = input('Playlist must be public, private or unlisted?')
        if privacy.lower() in ['public','private','unlisted']:
            check3 = False
            privacy = privacy.lower()
        else:
            print('Input a valid privacy status')

    try:
        conn.playlists().insert(
            part = "snippet,status",
            body = dict(
            snippet = dict(
                title = playlist_name,
                description = playlist_description
                ),
            status = dict(
            privacyStatus = privacy
                )
            )
        ).execute()

        print(f'\nNew playlist called {playlist_name} created succesfully.')

    except:
        print('\nAn error has occurred')


def show_playlists(conn: Resource) -> None:
    """
    Show playlists [Max 50] on channel id
    """
    
    clear()
    
    request = conn.playlists().list(
        part = "snippet",
        channelId = CHANNEL_ID,
        maxResults = 50
    )
    response = request.execute()
    playlists_quantity: int = response['pageInfo']['totalResults']

    playlists: list = []
    response = response['items']

    for j in range(len(response)):
        playlist_title: str = response[j]['snippet']['title']
        playlists.append(playlist_title)

    print(f'The user has {playlists_quantity} titled playlists on youtube:\n')
    for i in range(len(playlists)):
        print(f'{i + 1}. {playlists[i]}')


def add_song_to_playlist(conn: Resource) -> None:
    '''
    Add songs to a user playlist
    '''
    clear()

    #search the song
    print('Enter quit if you dont want to add more songs')
    song :str = input('Enter the song: ')
    tracks: list = []

    while song != 'quit':

        song = input('Enter the song: ')
        result = conn.search().list(
            q = song,
            part = 'snippet',
            max_results = 3,
        ).execute()

        tracks.append(result[0])
        
    #select a playlist
    numbers: list = []
    playlistitems :list = show_playlists(conn, _print=False)
    print('Choice a playlist to add the songs: ')

    for i in range(len(playlistitems)):
        print(i,  playlistitems[i]['snippet']['title'])
        numbers.append(i)

    number :int = -1
    while number not in numbers:
        number = int(input('Enter a number: '))

    playlist_id: str = playlistitems[number]['id']

    add_song(playlist_id, tracks)


    def add_song(playlist_id: str, tracks: list)->None:
    #add song to playlist
        videoIds = list(track['snippet']['videoId'] for track in tracks)

        for videoId in videoIds:
            request_body = {
                'snippet': {
                    'playlist_id' : playlist_id,
                    'resourseId': {
                        'kind': 'youtube#video',
                        'videoId': videoId,
                    } 
                }
            }

        conn.playlistItems().insert(
            part = 'snippet',
            body = request_body,
        ).execute()

    



