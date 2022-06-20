import tekore as tk
from tekore import Spotify
import os
import csv
import pathlib

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

    clear()

    playlists = Spotify.playlists(conn, USER_ID, 50, 0)
    
    if _print:
        print(f'The user has {playlists.total} titled playlists on Spotify:\n')
        for i in range(playlists.total):
            print(f'{i + 1}. {playlists.items[i].name}')
    else:
        return playlists.items

def export_playlist(conn: Spotify) -> None:
    """
    Export all track's data from certain playlist into a csv file
    """
    clear()

    playlistitems :list = show_playlists(conn, _print=False) # Get all playlists

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

    clear
    print('\nPlaylist exported successfully')   

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


def get_playlists_name(conn: Spotify):

    playlists = Spotify.playlists(conn, USER_ID)
    playlists_name_list = []
    
    for i in range(playlists.total):
        playlists_name_list.append(playlists.items[i].name)
            
    return playlists_name_list


def write_file(file, song):
    file.write(f'{song}\n')


def sync_to_youtube(conn: Spotify):
    print("\nSync playlist to Youtube\n")
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

    songs_not_in_youtube = []
    for song in spotify_songs:
        if song not in youtube_songs:
            songs_not_in_youtube.append(song)
            
    print(songs_not_in_youtube, 'songs_not_in_youtube') 
    
    file_spotify_to_youtube = open(path + 'spotify_to_youtube.csv','w')
    
    for song in songs_not_in_youtube:
        write_file(file_spotify_to_youtube, song)
        

    # add_song_to_playlist(conn)

    
