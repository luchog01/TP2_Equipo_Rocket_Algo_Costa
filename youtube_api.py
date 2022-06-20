import os
import re
import csv
import pathlib

path = str(pathlib.Path(__file__).parent.absolute()) + '\\files\\'

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
        
#########################
def get_response_playlist(conn):
    request = conn.playlists().list(
    part = "snippet",
    channelId = CHANNEL_ID,
    maxResults = 50
    )
    response = request.execute()
    playlists_quantity: int = response['pageInfo']['totalResults']

    response = response['items']
    
    return response


def get_playlists_name(conn):
    response = get_response_playlist(conn)
    
    playlists_name: list = []

    for j in range(len(response)):
        playlist_title: str = response[j]['snippet']['title']
        playlists_name.append(playlist_title)
        
    return playlists_name


def clean_titles(youtube_songs: list) -> list:
    """
    returns a list of song titles deleting the data that is not part of the song name of the received list
    """
    regex: str = "(?<=- ).*?(?=\(|\[|feat)"
    youtube_songs_clean: list = []
    for text in youtube_songs:
        if not re.findall(regex, text):
            title: list = re.findall('(?<=- ).*', text)
            youtube_songs_clean.append(title[0].title().strip())
        else:
            title: list = re.findall(regex, text)          
            youtube_songs_clean.append(title[0].title().strip())
            
    return youtube_songs_clean

def read_file(file):
    lines = []
    try:
        with open(file, newline='', encoding="UTF-8") as file_csv:
            csv_reader = csv.reader(file_csv, delimiter=',')
            next(csv_reader) # avoid reading the header
            for row in csv_reader:
                lines.append(row)
    except IOError:
        print("\nFile not found\n")
        
    return lines

def write_file(file, song):
    file.write(f'{song}\n')

def sync_to_spotify(conn: Resource):
    print("\nSync playlist to Spotify\n")
    # remember export playlists before sync
    print("Which playlist do you want to sync?\n")
    show_playlists(conn)

    playlist_number: int = int(input("\nSelect a playlist: "))
    playlist_name: list = get_playlists_name(conn)[playlist_number - 1]
    
    youtube_file: str = "files\youtube.csv"
    spotify_file: str = "files\spotify.csv"

    lines_youtube: list = read_file(youtube_file)
    lines_spotify: list = read_file(spotify_file)

    spotify_songs: list = []
    for line in lines_spotify:
        if line[0] == playlist_name:
            spotify_songs.append(line[1].strip())
       
    youtube_songs: list = []
    for line in lines_youtube:
        if line[0] == playlist_name:
            youtube_songs.append(line[1].strip())

    print(spotify_songs, 'spotify_songs')
    print(youtube_songs, 'youtube_songs')

    songs_not_in_spotify = []


    for song in youtube_songs:
        if song not in spotify_songs:
            songs_not_in_spotify.append(song)
            
    print(songs_not_in_spotify, 'songs_not_in_spotify') 
    
    file_youtube_to_spotify = open(path + 'youtube_to_spotify.csv','w')
    
    for song in songs_not_in_spotify:
        write_file(file_youtube_to_spotify, song)
        
    # add_song_to_playlist(conn)
