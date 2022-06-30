import tekore as tk
from tekore import Spotify
import os
import re
import csv
import pathlib
from time import sleep

path = str(pathlib.Path(__file__).parent.absolute()) + '\\files\\'
USER_ID = '31wehtihuhvriaasxyd5phnekdye'
CLIENT_ID = '5422aa04b10040e18ef47834e08ec9aa'
CLIENT_SECRET = 'a03bc8e3402949e480f4eb98036a230a'
REDIRECT_URI = 'https://example.com/callback' 
FILE_TEKORE = 'tekore.cfg' 


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


def login() -> Spotify:
    if os.path.exists(FILE_TEKORE):
        conf = tk.config_from_file(FILE_TEKORE, return_refresh=True)
        token = tk.refresh_user_token(*conf[:2], conf[3])
        spotify: Spotify = tk.Spotify(token)
    else:
        conf: tuple = (CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
        token = tk.prompt_for_user_token(*conf, scope=tk.scope.every)
        tk.config_to_file(FILE_TEKORE, conf + (token.refresh_token,))
        spotify: Spotify = tk.Spotify(token)

    return spotify


def new_playlist(conn: Spotify) -> None:
    """
    Create a new playlist in spotify asking for its name, description and privacy status
    """

    clear()

    check1: bool = True
    while check1:
        playlist_name :str = input('Input a name for your new playlist [Max 100 char]: ')
        if len(playlist_name) <= 100:
            check1 = False
        else:
            print('Playlist name must be less than 100 characters\n')

    check2: bool = True
    while check2:
        playlist_description :str = input('Input a description for your new playlist [Max 300 char]: ')
        if len(playlist_name) <= 300:
            check2 = False
        else:
            print('Playlist description must be less than 300 characters')

    check3: bool = True
    while check3:
        privacy: str = input('Playlist must be public or private?: ')
        if privacy.lower() in ['public','private']:
            check3 = False
            privacy = privacy.lower()

            if privacy == 'public':
                privacy_status: bool = True
            else:
                privacy_status: bool = False

        else:
            print('Input a valid privacy status')
    
    try:
        Spotify.playlist_create(conn, USER_ID, playlist_name,
                                privacy_status, playlist_description)
    except:
        print('\nAn error has occurred')


def show_playlists(conn: Spotify, _print :bool=True) -> None:
    """
    Show playlists [Max 50] on user id
    """

    clear()

    playlists = Spotify.playlists(conn, USER_ID, 50, 0)
    
    if _print:
        print(f'The user has {playlists.total} titled playlists on Spotify:\n')
        for i in range(playlists.total):
            print(f'{i + 1}. {playlists.items[i].name}')
    else:
        return playlists.items

def show_playlists(conn: Spotify, _print :bool=True) -> None:
    """
    Show playlists [Max 50] on user id
    """
    playlists = Spotify.playlists(conn, USER_ID, 50, 0)
    
    if _print:
        print(f'The user has {playlists.total} titled playlists on Spotify:\n')
        for i in range(playlists.total):
            print(f'{i + 1}. {playlists.items[i].name}')
    else:
        return playlists.items

def export_spotify_playlist(conn: Spotify, playlist_name = "") -> None:
    """
    Export all track's data from certain playlist into a csv file
    """
    playlistitems :list = show_playlists(conn, _print=False) # Get all playlists

    if playlist_name == "":
        # select a playlist
        print("Choice a playlist to export: ")
        for i in range(len(playlistitems)):
                print(f'{i}. {playlistitems[i].name}')
        option :str = ""
        while option not in [str(i) for i in range(len(playlistitems))]:
            option = input('Input a number: ')
        option = int(option)
        # get track's data from playlist 
        tracks :list = conn.playlist_items(playlistitems[option].id).items
    
    else:
        for i in range(len(playlistitems)):
            if playlistitems[i].name == playlist_name:
                # get track's data from playlist 
                option = i
                tracks :list = conn.playlist_items(playlistitems[option].id).items

    
    # fetch track's data into a list of lists
    tracks_data :list = []
    for track in tracks:
        name :str = str(track.track.name)
        id :str = str(track.track.id)
        artist :str = str(track.track.artists[0].name)
        album :str = str(track.track.album.name)
        duration :str = str(track.track.duration_ms)
        date :str = str(track.track.album.release_date)
        explicit :str = str(track.track.explicit)
        popularity :str = str(track.track.popularity)
        track_number :str = str(track.track.track_number)
        disc_number :str = str(track.track.disc_number)
        tracks_data.append([name, id, artist, album, duration, date, explicit, popularity, track_number, disc_number])

    # export to csv
    playlist_name = str(playlistitems[option].name).replace(' ', '_')
    with open(f'files/spotify_export_{playlist_name}.csv', 'w', encoding="utf-8") as f:
        f.write('name,id,artist,album,duration,date,explicit,popularity,track_number,disc_number\n')
        for track in tracks_data:
            try:
                f.write(','.join(track) + '\n')
            except:
                print('An error has occurred in track', track[0])

    print('Playlist exported successfully') 

def add_song_to_playlist(conn: Spotify) -> None:
    '''
    Add songs to a user playlist
    '''
    clear()

    #search the song
    print('Enter quit if you dont want to add more songs')
    song :str = input('Enter the song: ')
    tracks_uri: list = []

    while song != 'quit':
        result = conn.search(song, types= ('track',))[0].items[0]
        tracks_uri.append(result.uri)
        song = input('Enter the song: ')

    #select a playlist
    numbers: list = []
    playlistitems :list = show_playlists(conn, _print=False)
    print('Choice a playlist to add the songs: ')

    for i in range(len(playlistitems)):
        print(i, playlistitems[i].name)
        numbers.append(i)

    number :int = -1
    while number not in numbers:
        number = int(input('Enter a number: '))

    playlist_id: str = playlistitems[number].id
    playlist:str = playlistitems[number].name

    #add songs to playlist
    all_tracks :list = conn.playlist_items(playlist.uri).items

    conn.playlist_add(playlist_id = playlist_id, uris = tracks_uri, position=None)

    
    if tracks_uri in all_tracks:
        print('Songs successfully added')
    else:
        print('An error has occurred when trying to add the songs')   
    
def clean_titles(youtube_songs: list) -> list:
    regex_title: str = "(?<=- ).*?(?=\(|\[|feat)"
    regex_artist: str = ".*(?=-)"
    youtube_songs_clean: list = []
    for text in youtube_songs:
        if not re.findall(regex_title, text[1]):
            title: str = re.findall('(?<=- ).*', text[1])[0].title().strip()
            artist: str = re.findall(regex_artist, text[1])[0].strip()
            youtube_songs_clean.append([title, artist])
        else:
            title: str = re.findall(regex_title, text[1])[0].title().strip()
            artist: str = re.findall(regex_artist, text[1])[0].strip()
            youtube_songs_clean.append([title,artist])
            
    return youtube_songs_clean

def read_file_for_sync(file: str, playlist_name: str, platform: str):
    lines: list = []
    try:
        with open(file, newline='', encoding="UTF-8") as file_csv:
            csv_reader = csv.reader(file_csv, delimiter=',')
            next(csv_reader) # avoid reading the header
            for row in csv_reader:
                lines.append(row)
    except IOError:
        print(f"\nFile not found - Playlist {playlist_name} from {platform}\n")
        
    return lines

def get_songs_uri(track_id):  
    songs_uri: list = []
    for i in range(len(track_id)):
        songs_uri.append(playlist_songs = Spotify.track(track_id))
            
    return songs_uri

def read_file(file):
    lines: list = []
    with open(file, newline='', encoding="UTF-8") as file_csv:
        csv_reader = csv.reader(file_csv, delimiter=',')
        for row in csv_reader:
            lines.append(row)

    return lines

def get_spotify_playlist_id_by_playlist_name(conn: Spotify, playlist_name):
    playlists = Spotify.playlists(conn, USER_ID)
    playlists_id_list = []

    for i in range(playlists.total):
        if playlists.items[i].name == playlist_name:
            playlists_id_list.append(playlists.items[i].id)

    return playlists_id_list

def sync_to_youtube(conn: Spotify):
    """
    sync playlist adding songs not found in youtube to the youtube playlist
    """
    from youtube_api import get_yb_playlist_id_by_playlist_name, get_tracks, export_youtube_playlist, add_song_to_youtube_sync, login as login_youtube
    conn_youtube = login_youtube()
    
    print("\nSync playlist to Youtube\n")
    print("Which playlist do you want to sync?\n")
    
    show_playlists(conn, _print=True)    
    playlistitems :list = show_playlists(conn, _print=False) # get all playlists 
          
    # select an option
    option :str = ""
    while option not in [str(i) for i in range(len(playlistitems))]:
        option = input('\nSelect a playlist: ')
    option = int(option)
    
    playlist_name: str = Spotify.playlists(conn, USER_ID).items[option - 1].name
    
    # export playlists
    print('\nExporting Youtube playlist to csv...')
    sleep(2)
    export_youtube_playlist(conn_youtube, playlist_name)
    print('\nExporting Spotify playlist to csv...')  
    export_spotify_playlist(conn, playlist_name)
    sleep(2)
    
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
    # list songs that are not in youtube playlist
    youtube_songs = [x[0] for x in youtube_songs_artists]
    songs_not_in_youtube = [[x[0],x[1]] for x in spotify_songs_artists if x[0] not in youtube_songs]
   
    print('\nThe next songs are not in youtube playlist:')
    count_songs = 1
    for data in songs_not_in_youtube:
        print(f"{count_songs}. {data[0]} - {data[1]}")
        count_songs += 1
    
    # write songs_not_in_youtube in spotify_to_youtube.csv
    file_spotify_to_youtube = open(path + 'spotify_to_youtube.csv','w')
    for song in songs_not_in_youtube:
        file_spotify_to_youtube.write(f'{song[0]},{song[1]}\n')
    
    # read spotify_to_youtube.csv
    file_spotify_to_youtube = path + "spotify_to_youtube.csv"
    lines = read_file(file_spotify_to_youtube)
    
    # add songs not in youtube to youtube playlist  
    youtube_playlist_id = get_yb_playlist_id_by_playlist_name(conn_youtube, playlist_name)
    tracks = get_tracks(conn_youtube, lines)
    print(tracks)
    add_song_to_youtube_sync(youtube_playlist_id, tracks, conn_youtube)

    
def add_songs_sync_to_spotify(conn_spotify, lines, spotify_playlist_id):
    # get songs uris
    tracks_uris: list = []
    for line in lines:
        result_tracks = conn_spotify.search(f'{line[0]} artist:{line[1]}', types=('track',))[0].items[0]
        tracks_uris.append(result_tracks.uri)

    # add songs to playlist
    conn_spotify.playlist_add(playlist_id = spotify_playlist_id, uris = tracks_uris)


    


     
