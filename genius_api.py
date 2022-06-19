from http import client
from unicodedata import name
import lyricsgenius as lg
from lyricsgenius import OAuth2, Genius
import requests, os, platform, subprocess
import youtube_api as yt
import spotify_api as spt
from tekore import Spotify
from googleapiclient.discovery import Resource


CLIENT_ID_GENIUS = 'A_At5jqlqij-sYmSA2OSv14SKTKAYs_5Gj_VVKjZhs1v6Ojzx8KQ8mUqh0xyqrsG'
CLIENT_SECRET_GENIUS = 'Cjkb_GdeS8mfP6koCyvDVaNHjU86_uUqEsJ48B8KyNxA8wxxFDieEVxpK1bQ4gJ-zwLD-3eBmIPRWz4OdlMQ4g'
REDIRECT_URI_GENIUS = 'http://example.com/callback'
CLIENT_ACCESS_TOKEN_GENIUS = 'O3AGX5hNh3cYFYGxbp6Nv1L1L_6W7QEHsC_XaIzGWTyYDXfEwt0K2YOjHAUdBPTF'


def make_word_cloud() -> None:
#app :str, conn_yt: Resource, conn_spt: Spotify
    yt.clear()
    #Read the file from yt/spt
    # if app == 'Youtube':
    #     yt.show_playlists(conn_yt)
    #     playlist: str = input('Which playlist do you want to make a word cloud?: ')    
    
    
    
    # elif app == 'Spotify':
    #     spt.show_playlists(conn_spt)
    #     playlist: str = input('Which playlist do you want to make a word cloud?: ')

    genius = Genius(CLIENT_ACCESS_TOKEN_GENIUS, verbose = False, remove_section_headers = True)
    
    print('Doing the word cloud, wait a minute...')
    
    #songs = [[title1, artist1], [title2,artist2]]
    songs = [['new rules', 'dua lipa'], ['levitating (remix)','dua lipa'], ['imagine', 'ariana grande']]
    lyrics: list = []
    for song in songs:
        
        lyric = genius.search_song(song[0], song[1])
        lyric = lyric.to_text()        
        #Adlibs filter
        check = False
        while not check:
            first = lyric.find('(')
            second = lyric.find(')')

            if first != -1:
                lyric = lyric[:first] + lyric[second + 1:]
            elif first == -1:
                check = True

        lyrics.append(lyric)
    lyrics_string = ' '.join(lyrics)
    #WordCloud
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

    with open('playlist_cloud.png', 'wb') as file:
        file.write(resp.content)
    
    #Open a window with playlist_cloud.png
    if platform.system() == 'Darwin':       # macOS
        subprocess.call(('open', 'playlist_cloud.png'))
    elif platform.system() == 'Windows':    # Windows
        os.startfile('playlist_cloud.png')
    else:                                   # linux variants
        subprocess.call(('xdg-open', 'playlist_cloud.png'))
    
make_word_cloud()