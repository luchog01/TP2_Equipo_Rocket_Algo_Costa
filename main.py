from importlib.resources import Resource
import spotify_api as spotify
import youtube_api as youtube
from tekore import Spotify

def select_plataform(plataform:str) -> None:
    if plataform == "spotify":
        pass # return spotify service
    elif plataform == "youtube":
        pass # return youtube service
    else:
        print("Plataform not supported")

def show_menu() -> None:
    print("""
MENU\n
1. Log in - YouTube
2. Log in - Spotify
3. Exit
""")

def show_youtube_menu() -> None:
    print("""
YOUTUBE MENU\n
1. New playlist
2. Add song to playlist
3. Show playlists
4. Export playlists
5. Sync to Spotify
6. Make a word cloud
7. Exit
""")

def show_spotify_menu() -> None:
    print("""
SPOTIFY MENU\n
1. New playlist
2. Add song to playlist
3. Show playlists
4. Export playlists
5. Sync to Youtube
6. Make a word cloud
7. Exit
""")

def main():
    option: str = ""

    while option != "3":
        show_menu()
        option = input("Select an option: ")
        
        if option == "1":
            try:
                conn: Resource = youtube.login()
                print("Successfully logged in\n")
            except:
                print("\nAn error has occurred when trying to connect with Youtube\n")
                option = "7"

            while option != "7":
                show_youtube_menu()
                option = input("Select an option: ")
                if option == "1":
                    youtube.new_playlist(conn)
                elif option == "2":
                    youtube.add_song_to_playlist(conn)
                elif option == "3":
                    youtube.show_playlists(conn)
                elif option == "4":
                    youtube.export_playlists(conn)
                elif option == "5":
                    youtube.sync_to_spotify(conn)
                elif option == "6":
                    youtube.make_word_cloud(conn)
                elif option not in ["1","2","3","4","5","6","7"]:
                    print("Not valid option")

        elif option == "2":
            try:
                conn:Spotify = spotify.login()
                print("Successfully logged in\n")
            except:
                print("\nAn error has occurred when trying to connect with Spotify\n")
                option = "7"
            while option != "7":
                show_spotify_menu()
                option = input("Select an option: ")
                if option == "1":
                    spotify.new_playlist(conn)
                elif option == "2":
                    spotify.add_song_to_playlist(conn)
                elif option == "3":
                    spotify.show_playlists(conn)
                elif option == "4":
                    spotify.export_playlists(conn)
                elif option == "5":
                    spotify.sync_to_youtube(conn)
                elif option == "6":
                    spotify.make_word_cloud(conn)
                elif option not in ["1","2","3","4","5","6","7"]:
                    print("Not valid option")

        elif option not in ['1','2','3']:
            print("Option not supported")
            
    else:
        print('Bye, \'Loco Mauro\'')


main()
