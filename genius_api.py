
from lyricsgenius import Genius
import requests, os, platform, subprocess
import youtube_api as yt
import spotify_api as spt
from tekore import Spotify
from googleapiclient.discovery import Resource
from youtube_api import clear

CLIENT_ID_GENIUS = 'A_At5jqlqij-sYmSA2OSv14SKTKAYs_5Gj_VVKjZhs1v6Ojzx8KQ8mUqh0xyqrsG'
CLIENT_SECRET_GENIUS = 'Cjkb_GdeS8mfP6koCyvDVaNHjU86_uUqEsJ48B8KyNxA8wxxFDieEVxpK1bQ4gJ-zwLD-3eBmIPRWz4OdlMQ4g'
REDIRECT_URI_GENIUS = 'http://example.com/callback'
CLIENT_ACCESS_TOKEN_GENIUS = 'tR_Wo4i2UkEUIj5zmrtxEN6aY559veZ_UxtL_AKJxPBUC1qSwiAG4-VMrbWZ1L12'



def get_tracks_info(app :str, conn) -> list:

    clear()
    #Read the file from yt/spt
    if app == 'Youtube':
        response = yt.show_playlists(conn, _print = False)
        playlists_quantity: int = len(response)
        yt.show_playlists(conn, _print = True)
        
        playlist_number: int = 0
        while playlist_number not in range(1,playlists_quantity + 1):
            playlist_number: int = int(input('Which playlist do you want to make a word cloud? [Input the number]: '))
        clear()
        playlist_id: str = response[playlist_number - 1]['id']
        
        track_info: list = yt.getTracksInfo(conn, playlist_id) 
        if track_info == []:
                raise IndexError('Empty playlist')
            
        remix = False
        songs = []
        for track in track_info:
            title: str = track[0].lower()
            artist: str = track[1].lower()
            #Title filter
            if artist.endswith(' - topic'):
                    artist = artist[:len(artist) - 8]

            if artist.endswith('vevo'):
                artist = artist[:len(artist) - 4]
                
            if 'remix' in title.lower():
                remix = True
                title.replac('remix','')

            check = False
            while not check:
                first = title.find('(')
                second = title.find(')')

                if first != -1:
                    title = title[:first] + title[second + 1:]
                elif first == -1:
                    check = True
                    
            if remix:
                title = title + 'remix'
            songs.append([title, artist])
        return songs
        
    elif app == 'Spotify':
        response = spt.show_playlists(conn, _print = False)
        playlists_quantity: int = len(response)
        spt.show_playlists(conn, _print = True)
        
        playlist_number: int = 0
        while playlist_number not in range(1,playlists_quantity + 1):
            playlist_number: int = int(input('Which playlist do you want to make a word cloud? [Input the number]: '))

        clear()
        playlist_id: str = response[playlist_number - 1].id
        track_info :list = conn.playlist_items(playlist_id).items
        if track_info == []:
                raise IndexError('Empty playlist')
        
        songs: list = []
        for track in track_info:
            title: str = (str(track.track.name)).lower()
            artist: str = (str(track.track.artists[0].name)).lower()
            songs.append([title, artist])
        return songs 

def get_lyrics(songs: list, only_get: bool) -> list:
    try:
        genius = Genius(CLIENT_ACCESS_TOKEN_GENIUS, verbose = True, remove_section_headers = True)
    
        lyrics: list = []
        for song in songs: #Search lyrics
            try: #Try searching with the artist name
                lyric = genius.search_song(song[0], song[1])
                lyric = lyric.to_text()
            except:
                try: #Try searching without the artist name
                    lyric = genius.search_song(song[0])
                    lyric = lyric.to_text()
                except:
                    #wrong song? or wrong artist?, manual search
                    title_ok: str = ''
                    while title_ok not in ['y','n']:
                        title_ok = input(f'Is the name of this song okay? : {song[0]}\n[y/n]: ')
                        title_ok = title_ok.lower()
                        
                    if title_ok == 'n':
                        new_title: str = input('Input the full name of the song : ')
                    else:
                        new_title: str = song[0]
                        
                    artist_ok: str = ''
                    while artist_ok not in ['y','n']:
                        artist_ok = input(f'Is the name of this song okay? : {song[1]}\n[y/n]: ')
                        artist_ok = artist_ok.lower()
                        
                    if artist_ok == 'n':
                        new_artist: str = input('Input the full name of the artist : ')
                    else:
                        new_artist: str = song[1]
                        
                    songs2: list = [[new_title, new_artist]]
                    lyric = get_lyrics(songs2, only_get = True)
                    lyric = ''.join(lyric)

            #lyrics filter
            if not only_get:
                check = False
                while not check:
                    first = lyric.find('(')
                    second = lyric.find(')')

                    if first != -1:
                        lyric = lyric[:first] + lyric[second + 1:]
                    elif first == -1:
                        check = True
                        
                lyric = lyric.replace('\n',' ')
                cut = (lyric.lower()).find('lyrics')
                lyric = lyric[cut + 7:]
                lyrics.append(lyric)
        return lyrics
    except:
        print('An error has occurred while trying to connect to the lyrics server')


def make_word_cloud(app :str, conn) -> None:
    try:  
        lyrics: list = get_lyrics(get_tracks_info(app, conn), only_get = False)
        lyrics_string = ' '.join(lyrics)
        
        print('Doing the word cloud, wait a minute...')
        resp = requests.post('https://quickchart.io/wordcloud', json={
            'format': 'png',
            'width': 1920,
            'height': 1080,
            'fontScale': 15,
            'scale': 'linear',
            'removeStopwords': True,
            'minWordLength': 4,
            'text': lyrics_string,
        })

        with open('files\playlist_cloud.png', 'wb') as file:
            file.write(resp.content)
        
        #Open a window with playlist_cloud.png
        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', 'files\playlist_cloud.png'))
        elif platform.system() == 'Windows':    # Windows
            os.startfile('files\playlist_cloud.png')
        else:                                   # linux variants
            subprocess.call(('xdg-open', 'files\playlist_cloud.png'))
            
    except IndexError:
        print('We can\'t make a word cloud out of an empty playlist')
    except:
        print('An error occurred while trying to create the word cloud')