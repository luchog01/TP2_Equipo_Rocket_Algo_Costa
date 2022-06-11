import os

from io import TextIOWrapper
from googleapiclient.discovery import Resource, build
from googleapiclient.errors import HttpError, Error
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

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
    return build('youtube', 'v3', credentials=generar_credenciales())
