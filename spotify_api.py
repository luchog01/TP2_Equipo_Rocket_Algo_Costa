import tekore as tk
from tekore import Spotify
import os

CLIENT_ID = '5422aa04b10040e18ef47834e08ec9aa'
CLIENT_SECRET = 'a03bc8e3402949e480f4eb98036a230a'
REDIRECT_URI = 'https://example.com/callback' 
FILE_TEKORE = 'tekore.cfg' 


def login() -> Spotify:
    if os.path.exists(FILE_TEKORE):
        conf = tk.config_from_file(FILE_TEKORE, return_refresh=True)
        token = tk.refresh_user_token(*conf[:2], conf[3])
        spotify = tk.Spotify(token)
    else:
        conf: tuple = (CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
        token = tk.prompt_for_user_token(*conf, scope=tk.scope.every)
        tk.config_to_file(FILE_TEKORE, conf + (token.refresh_token,))
        spotify: Spotify = tk.Spotify(token)

    return spotify
   