import os
import tekore as tk

from tekore import RefreshingToken, Spotify


CLIENT_ID = 'YOUR_CLIENT_ID'
CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
REDIRECT_URI = 'https://example.com/callback'  
ARCHIVO_TEKORE = 'tekore.cfg'


def cargar_token():

    token: RefreshingToken = None

    if os.path.exists(ARCHIVO_TEKORE):
        
        configuracion: tuple = tk.config_from_file(ARCHIVO_TEKORE, return_refresh=True)
        token = tk.refresh_user_token(*configuracion[:2], configuracion[3])        

    return token


def guardar_token(configuracion: tuple, token: RefreshingToken) -> None:

    tk.config_to_file(ARCHIVO_TEKORE, configuracion + (token.refresh_token,))


def es_token_invalido(token: RefreshingToken) -> bool:

    return not token


def autorizar_credenciales(configuracion: tuple) -> RefreshingToken:

    token = tk.prompt_for_user_token(*configuracion, scope=tk.scope.every)

    return token


def generar_token() -> RefreshingToken:

    token: RefreshingToken = cargar_token()
    configuracion = (CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)

    if es_token_invalido(token):

        token = autorizar_credenciales(configuracion)

        guardar_token(configuracion, token)

    return token


def obtener_servicio() -> Spotify:
    """
    Creador de la conexion a la API Spotify
    """
    return tk.Spotify(generar_token())
