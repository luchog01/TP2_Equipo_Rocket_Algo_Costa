import os
import csv
import pathlib

from googleapiclient.discovery import Resource, build
from googleapiclient.errors import HttpError, Error
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from requests import request
from time import sleep



path = str(pathlib.Path(__file__).parent.absolute()) + '\\files\\'

CHANNEL_ID = 'UCxz7Qo_DeuK-LzHfK2KMo7w'

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
        privacy: str = input('Playlist must be public, private or unlisted? ')
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


def show_playlists(conn: Resource, _print: bool = True) -> None:
    """
    Show playlists [Max 50] on channel id
    """    
    request = conn.playlists().list(
        part = "snippet",
        channelId = CHANNEL_ID,
        maxResults = 50
    )
    response = request.execute()
    playlists_quantity: int = response['pageInfo']['totalResults']

    playlists: list = []
    response = response['items']

    if _print:
        for j in range(len(response)):
            playlist_title: str = response[j]['snippet']['title']
            playlists.append(playlist_title)

        print(f'The user has {playlists_quantity} titled playlists on youtube:\n')
        for i in range(len(playlists)):
            print(f'{i + 1}. {playlists[i]}')
    else:
        return response


def getTracksInfo(conn: Resource, playlist_id: str) -> list:
    """
    Get all tracks info from certain playlist
    """
    tracks_info: list = []

    request = conn.playlistItems().list(
        part = "snippet",
        playlistId = playlist_id,
        maxResults = 50
    )
    response = request.execute()

    response = response['items']

    # retrive all tracks info from youtube API response and fetch them into a list of list for every track
    for i in range(len(response)):
        track_title: str = response[i]['snippet']['title']
        videoOwner: str = response[i]['snippet']['videoOwnerChannelTitle']
        video_id: str = response[i]['snippet']['resourceId']['videoId']
        published_id: str = response[i]['snippet']['publishedAt']
        track_id: str = response[i]['id']
        etag: str = response[i]['etag']
        videoOwnerId: str = response[i]['snippet']['videoOwnerChannelId']
        description: str = str(response[i]['snippet']['description']).replace('\n', ' ') # remove new lines from description
        track_type: str = response[i]['snippet']['resourceId']['kind']
        jpg_link :str = response[i]['snippet']['thumbnails']['medium']['url']
        
        tracks_info.append([track_title, videoOwner, video_id, published_id, track_id, etag, videoOwnerId, description, track_type, jpg_link])

    return tracks_info


def add_song(playlist_id: str, tracks: list, conn: Resource) -> None:
    #add songs to playlist
  
    videoIds: list = []

    for i in range(len(tracks)):
        track = tracks[i]
        videoId = track['id']['videoId']
        videoIds.append(videoId)

    for videoId in videoIds:
        playlists_insert_response = conn.playlistItems().insert(
        part="snippet",
        body=dict(
        snippet=dict(
            playlistId=playlist_id,
            resourceId=dict(
            kind="youtube#video",
            videoId=videoId,
            )
            )
        )
    ).execute()
    print ("\nNew playlist item id: %s" % playlists_insert_response["id"] )


def add_songs_sync_to_youtube(playlist_id: str, tracks: list, conn: Resource) -> None:
    #add songs to playlist

    videoIds: list = []
    for i in range(len(tracks)):
        track = tracks[i]
        videoId = track['items'][0]['id']['videoId']
        videoIds.append(videoId)

    for videoId in videoIds:
        playlists_insert_response = conn.playlistItems().insert(
        part="snippet",
        body=dict(
        snippet=dict(
            playlistId=playlist_id,
            resourceId=dict(
            kind="youtube#video",
            videoId=videoId,
            )
            )
        )
    ).execute()


def add_song_to_playlist(conn: Resource) -> None:
    '''
    Add songs to a user playlist
    '''
    clear()

    #search the song
    print('Enter quit if you dont want to add more songs')
    song :str = input('\nEnter the song: ')
    tracks: list = []

    while song != 'quit':

        result = conn.search().list(
            q = song,
            part = 'snippet',
            maxResults = 3,
            type = 'video',
        ).execute()
        songs :list = result['items']
        
        options: list = []
        for i in range(len(songs)):
            print(i, songs[i]['snippet']['title'])
            options.append(i)

        option :int = -1
        while option not in options:
            option = int(input('\nEnter a number: '))

        song = songs[option]
        tracks.append(song)
        song :str = input('\nEnter a song: ')
    

    #select a playlist
    numbers: list = []
    playlistitems :list = show_playlists(conn, _print=False)
    print('\nChoice a playlist to add the songs: ')

    for i in range(len(playlistitems)):
        print(i,  playlistitems[i]['snippet']['title'])
        numbers.append(i)

    number :int = -1
    while number not in numbers:
        number = int(input('\nEnter a number: '))

    playlist_id: str = playlistitems[number]['id']

    add_song(playlist_id, tracks, conn)


def export_youtube_playlist(conn: Resource, playlist_name: str = "") -> None:
    """
    Export all track's data from certain playlist into a csv file   
    """
    # get playlist id from playlist name
    response = show_playlists(conn)

    if playlist_name == "":
        # get playlists names
        playlists :list = []
        print("Choice a playlist to export: ")
        for j in range(len(response)):
                playlist_title: str = response[j]['snippet']['title']
                print(f'{j}. {playlist_title}')
                playlists.append(playlist_title)

        # select a playlist name
        option :str = ""
        while option not in [str(i) for i in range(len(playlists))]:
            option = input('Input a number: ')

        playlist_name = playlists[int(option)] 


    # get playlist id using playlist name
    for i in range(len(response)):
        if response[i]['snippet']['title'] == playlist_name: # if playlist name is the same as the one selected
            playlist_id = response[i]['id']
    
            tracks_info: list = getTracksInfo(conn, playlist_id) # get tracks info
            
            # create a csv file with all tracks info
            with open(f'files/youtube_export_{playlist_name}.csv', 'w', newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Track title', 'Video owner', 'Video id', 'Published date', 'Track id', 'Etag', 'Video owner id', 'Description', 'Track type', 'Jpg link'])
                for i in range(len(tracks_info)):
                    try:
                        writer.writerow(tracks_info[i])
                    except Exception as e:
                        print(f"Error writing track {tracks_info[i][0]}, error msg: {e}")

    print("Playlist exported successfully")


def get_yb_playlist_id_by_playlist_name(conn,playlist_name):
    response = show_playlists(conn, _print=False)   
    for j in range(len(response)):
        if response[j]['snippet']['title'] == playlist_name:
            playlist_id: str = response[j]['id']

    return playlist_id


def sync_to_spotify(conn: Resource):
    """
    sync playlist adding songs not found in spotify to the spotify playlist
    """
    from spotify_api import add_songs_sync_to_spotify, clean_titles, export_spotify_playlist, get_spotify_playlist_id_by_playlist_name, read_file, read_file_for_sync
    from spotify_api import login as login_spotify
    conn_spotify: Resource = login_spotify()
    
    print("\nSync playlist to Spotify\n")
    print("Which playlist do you want to sync?\n")

    response = show_playlists(conn, _print=False)
    show_playlists(conn, _print=True)
    total_playlists = len(response)

    # input playlist number
    playlist_number: int = 0
    while playlist_number not in range(1, total_playlists + 1):
        try:
            playlist_number: int = int(input('\nSelect a playlist: '))
        except:
            print('Invalid Option')
    
    playlist_name: str = response[playlist_number - 1]['snippet']['title']
    
    # export playlists
    print('\nExporting Youtube playlist to csv...')
    sleep(2)
    export_youtube_playlist(conn, playlist_name)
    print('\nExporting Spotify playlist to csv...')  
    export_spotify_playlist(conn_spotify, playlist_name)
    sleep(2)
    
    # files data
    youtube_file: str = path + f"youtube_export_{playlist_name}.csv"
    spotify_file: str = path + f"spotify_export_{playlist_name}.csv"
    lines_youtube: list = read_file_for_sync(youtube_file, playlist_name, 'Youtube')
    lines_spotify: list = read_file_for_sync(spotify_file, playlist_name, 'Spotify')
    
    # list all songs,artists of the chosen spotify playlist
    spotify_songs_artists: list = []
    for line in lines_spotify:
        spotify_songs_artists.append([line[0].strip().title(), line[2].strip()]) #[[name. artist]]
        
    # list all songs,artists of the chosen spotify playlist
    youtube_songs_artists: list = []
    for line in lines_youtube:
        if line != []:
            youtube_songs_artists.append([line[1].strip().title(), line[0].strip()])
    youtube_songs_artists = clean_titles(youtube_songs_artists)

    # list songs that are not in spotify playlist
    spotify_songs: list = [x[0] for x in spotify_songs_artists]
    songs_not_in_spotify: list = [[x[0],x[1]] for x in youtube_songs_artists if x[0] not in spotify_songs]
    print('\nThe next songs are not in the spotify playlist:')
    count_songs: int = 1
    for data in songs_not_in_spotify:
        print(f"{count_songs}. {data[0]} - {data[1]}")
        count_songs += 1
    sleep(2)
    
    # write songs_not_in_spotify in youtube_to_spotify.csv
    file_youtube_to_spotify = open(path + 'youtube_to_spotify.csv','w')
    for song in songs_not_in_spotify:
        file_youtube_to_spotify.write(f'{song[0]},{song[1]}\n')
        
    # read youtube_to_spotify.csv
    file_youtube_to_spotify = path + "youtube_to_spotify.csv"
    lines = read_file(file_youtube_to_spotify)
    
    # add songs not in spotify to spotify playlist
    spotify_playlist_id = get_spotify_playlist_id_by_playlist_name(conn_spotify, playlist_name)[0]
    print('\nAdding songs...')
    add_songs_sync_to_spotify(conn_spotify, lines, spotify_playlist_id)
    print('Songs added.')

    
def get_tracks(conn, lines):
    tracks = []
    for line in lines:
        
        result = conn.search().list(
                q = line[0],
                part = 'snippet',
                maxResults = 1,
                type = 'video',
            ).execute()
        
        tracks.append(result)

    return tracks

