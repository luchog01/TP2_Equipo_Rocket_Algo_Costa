from lyricsgenius import Genius
import requests, os, platform, subprocess
import youtube_api as yt
import spotify_api as spt
from youtube_api import clear
from googleapiclient.discovery import Resource
from tekore import Spotify

CLIENT_ID_GENIUS = '2dqdSoz3Sbq5hZqMQ5wc87hgR0JKvp0yHjGw0ZolfbVRIu32nth6bMzZPutRgszt'
CLIENT_SECRET_GENIUS = 'oQbNvvO0mbOkhK6UX8-MyyrpmJpN66T2qh1T6PX7iPXNIv6RK9uR17ZOfSfGkqUrIh9rNz8jVCTAZE63TEt9sw'
REDIRECT_URI_GENIUS = 'http://example.com/callback'
CLIENT_ACCESS_TOKEN_GENIUS = 'aaaFW4ev8jSzuA8p0YzfWN7u4SPVLZqy9-ga4xqYieu5CxP2fvvT-swDQVODAuk1'

def song_filter(title: str, artist: str) -> list:
    """
    Filter the title and artist of each song
    """
    if artist.endswith(' - topic'):
        artist = artist[:len(artist) - 8]

    if artist.endswith('vevo'):
        artist = artist[:len(artist) - 4]
        
    remix: bool = False
    if 'remix' in title.lower():
        remix = True
        title.replace('remix','')

    check: bool = False
    while not check:
        first: int = title.find('(')
        second: int = title.find(')')

        if first != -1:
            title = title[:first] + title[second + 1:]
        elif first == -1:
            check = True
            
    if remix:
        title = title + 'remix'
    song: list = [title,artist]
    return song


def get_tracks_info(app :str, conn) -> list:
    """
    Search for the title and artist of each song in a youtube/spotify playlist
    """
    clear()
    #Read the file from yt/spt
    if app == 'Youtube':
        response: Resource = yt.show_playlists(conn, _print = False)
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
            
        songs: list = []
        for track in track_info:
            title: str = track[0].lower()
            artist: str = track[1].lower()
            songs.append(song_filter(title, artist))
        return songs
        
    elif app == 'Spotify':
        response: Spotify = spt.show_playlists(conn, _print = False)
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
            songs.append(song_filter(title, artist))
        return songs 

def get_lyrics(songs: list, only_get: bool) -> list:
    """
    Get the lyrics of each song
    """
    genius: Genius = Genius(CLIENT_ACCESS_TOKEN_GENIUS, verbose = False, remove_section_headers = True)
        
    lyrics: list = []
    print('Searching lyrics...')
    for song in songs: #Search lyrics
        try: #Try searching with the artist name
            lyric: Genius = genius.search_song(song[0], song[1])
            lyric: str = lyric.to_text()
        except:
            try: #Try searching without the artist name
                lyric: Genius = genius.search_song(song[0])
                lyric: str = lyric.to_text()

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
                lyric: list = get_lyrics(songs2, only_get = True)

        #lyrics filter
        if not only_get:
            if type(lyric) == list:
                lyric: str = ''.join(lyric)
            check: bool = False
            while not check:
                first: int = lyric.find('(')
                second: int = lyric.find(')')

                if first != -1:
                    lyric = lyric[:first] + lyric[second + 1:]
                elif first == -1:
                    check = True

            lyric = lyric.replace('\n',' ')
            cut: int = (lyric.lower()).find('lyrics')
            lyric = lyric[cut + 7:]
            lyrics.append(lyric)
            
        if only_get:
            lyric = ''.join(lyric)
            lyrics.append(lyric)
    return lyrics


def top10_words(lyrics: str) -> None:
    """
    Print a top 10 most used words in all the playlist
    """
    #Filter
    lyrics = lyrics.lower()
    lyrics_list :list = lyrics.split(' ')
    filter_list: list = [
        '',' ','-','i','it','you','we','he','she',
        'the','me','on','and',',','that','your','me','my'
        'que','y','a','no','la','el','un','in','at','do','do\'t',
        'de','en','i\'m','with','you\'re'
        ]
    lyrics_list2: list = [word for word in lyrics_list if word not in filter_list]
    #Sort
    dicc: dict = {word:lyrics_list2.count(word) for word in lyrics_list2}
    sorted_tuples: tuple = sorted(dicc.items(), key=lambda item: item[1], reverse = True)
    sorted_list: list = [[k, v] for k, v in sorted_tuples]
    #Print rank
    if len(sorted_list) > 10:
        max_rank: int = 10
    elif len(sorted_list) < 10:
        max_rank: int = len(sorted_list)
    
    for i in range(max_rank):
        print(f'<{sorted_list[i][0]}> repeats {sorted_list[i][1]} times in all the playlist')


def make_word_cloud(app :str, conn) -> None:
    """
    Do a word cloud with all the lyrics
    """
    try:  
        lyrics: list = get_lyrics(get_tracks_info(app, conn), only_get = False)
        lyrics_string: str = ' '.join(lyrics)
        
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
        
        top10_words(lyrics_string)
        input('\nInput any key to return menu ')
            
    except IndexError:
        print('We can\'t make a word cloud out of an empty playlist')
    except:
        print('An error occurred while trying to create the word cloud')
