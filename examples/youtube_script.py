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


def cargar_credenciales() -> Credentials:

    credencial: Credentials = None

    if os.path.exists(ARCHIVO_TOKEN):
        
        archivo: TextIOWrapper = open(ARCHIVO_TOKEN, 'r', encoding='utf-8')

        try:
            with archivo:
                credencial = Credentials.from_authorized_user_file(ARCHIVO_TOKEN, SCOPES)

        except IOError:
            print('\nNo se pudo leer el archivo: ', ARCHIVO_TOKEN)
        
        finally:
            archivo.close()            

    return credencial


def guardar_credenciales(credencial: Credentials) -> None:

    archivo: TextIOWrapper = open(ARCHIVO_TOKEN, 'w', encoding='utf-8')

    try:
        with archivo:
            archivo.write(credencial.to_json())

    except IOError:
        print('\nNo se pudo escribir el archivo: ', ARCHIVO_TOKEN)

    finally:
        archivo.close()             


def son_credenciales_invalidas(credencial: Credentials) -> bool:

    return not credencial or not credencial.valid


def son_credenciales_expiradas(credencial: Credentials) -> bool:

    return credencial and credencial.expired and credencial.refresh_token


def autorizar_credenciales() -> Credentials:

    flow: InstalledAppFlow = InstalledAppFlow.from_client_secrets_file(ARCHIVO_SECRET_CLIENT, SCOPES)

    return flow.run_local_server(open_browser=False, port=0)


def generar_credenciales() -> Credentials:

    credencial: Credentials = cargar_credenciales()

    if son_credenciales_invalidas(credencial):

        if son_credenciales_expiradas(credencial):
            credencial.refresh(Request())

        else:
            credencial = autorizar_credenciales()

        guardar_credenciales(credencial)

    return credencial


def obtener_servicio() -> Resource:
    """
    Creador de la conexion a la API Youtube
    """
    return build("youtube", "v3", credentials=generar_credenciales())

# NUESTRO CODIGO

def getCanal(username) -> None:
    """
    Obtiene canal
    """
    conn = obtener_servicio()

    request = conn.channels().list(
        part='statistics',
        forUsername=username
    )

    response = request.execute()
    return response



def crearPlaylist(nombrePlaylist, descripcionPlaylist) -> None:
    """
    Crea playlist
    """
    conn = obtener_servicio()

    playlists_insert_response = conn.playlists().insert(
        part="snippet,status",
        body=dict(
        snippet=dict(
            title=nombrePlaylist,
            description=descripcionPlaylist
            ),
        status=dict(
        privacyStatus="private"
            )
        )
    ).execute()
    print ("New playlist id: %s" % playlists_insert_response["id"])


def agregarVideo(idPlaylist, idVideo) -> None:
    """
    Agrega video a playlist
    """
    conn = obtener_servicio()

    playlists_insert_response = conn.playlistItems().insert(
        part="snippet",
        body=dict(
        snippet=dict(
            playlistId=idPlaylist,
            resourceId=dict(
            kind="youtube#video",
            videoId=idVideo
            )
            )
        )
    ).execute()
    print ("New playlist item id: %s" % playlists_insert_response["id"])

def obtenerVideos(idPlaylist) -> None:
    """
    Obtiene videos de playlist
    """
    videos:list = [] # [["id","titulo"],["u43b2j","Top 10 ..."]]

    conn = obtener_servicio()

    request = conn.playlistItems().list(
        part="snippet",
        playlistId=idPlaylist
    )
    response = request.execute()
    response = response["items"]
    for i in response:
        item_video = []
        item_video.append(i["snippet"]["resourceId"]["videoId"])
        item_video.append(i["snippet"]["title"])
        videos.append(item_video)
    return videos

def obtenerPlaylists() -> None:
    """
    Obtiene playlists
    """
    playlists:list = [] # [["id","titulo"],["u43b2j","Top 10 ..."]]

    conn = obtener_servicio()

    request = conn.playlists().list(
        part="snippet",
        mine=True
    )
    response = request.execute()
    response = response["items"]
    for i in response:
        item_playlist = []
        item_playlist.append(i["id"])
        item_playlist.append(i["snippet"]["title"])
        playlists.append(item_playlist)
    return playlists

def obtenerVideosPlaylist():
    playlists_tree = {} # {title: { id: "313", elementos: [idVideo, idVideo, ...]}, ...}
    playlists = obtenerPlaylists()
    for i in playlists:
        playlists_tree[i[1]] = {"id": i[0], "elementos": obtenerVideos(i[0])}
    return playlists_tree
    
# def getVideo(videoId) -> None:
#     """
#     Obtiene video
#     """
#     conn = obtener_servicio()

#     request = conn.videos().list(
#         part='statistics',
#         id=videoId
#     )

#     response = request.execute()
#     return response

# def getPlaylist(playlistId) -> None:
#     """
#     Obtiene playlist
#     """
#     conn = obtener_servicio()

#     request = conn.playlistItems().list(
#         part='statistics',
#         playlistId=playlistId
#     )

#     response = request.execute()
#     return response
# youtube pop rock electro  1 usuario
# 3 sub-usuarios -> su1:rock su2:pop, electro
# hola q user sos? su1 
# print(getCanal('PewDiePie'))
#print(crearPlaylist("Primera Playlist", "Buena Playlist"))
#print(agregarVideo("PLIG13vm2QTYwCFv8lDl0SOiq1Tjwie_Ko", "k2qgadSvNyU"))
# print(obtenerVideos("PLIG13vm2QTYwCFv8lDl0SOiq1Tjwie_Ko"))
# print(obtenerPlaylists())
# print(obtenerVideosPlaylist())

print(obtener_servicio())
