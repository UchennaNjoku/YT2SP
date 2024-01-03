from spotipy import util 
import requests
from pprint import pprint
from os import getenv
from dotenv import load_dotenv


# load_dotenv()

# SPOTIPY_USER_ID = getenv('SPOTIPY_USER_ID', None)
# assert SPOTIPY_USER_ID
# SPOTIPY_CLIENT_ID = getenv('SPOTIPY_CLIENT_ID', None)
# assert SPOTIPY_CLIENT_ID
# SPOTIPY_CLIENT_SECRET = getenv('SPOTIPY_CLIENT_SECRET', None)
# assert SPOTIPY_CLIENT_SECRET

# checking the env files
# print(SPOTIPY_USER_ID, SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET)

class Spotify:

    load_dotenv()

    def __init__(self):
        self.scope = 'playlist-modify-public'
        self.username = getenv('SPOTIPY_USER_ID', None)
        self.user_id = getenv('SPOTIPY_USER_ID', None)
        self.client_id = getenv('SPOTIPY_CLIENT_ID', None)
        self.client_secret = getenv('SPOTIPY_CLIENT_SECRET', None)
        self.redirect_uri = getenv('REDIRECT_URI', None)
        # self.redirect_uri = 'http://localhost:8888/callback'

    @property
    def token(self):
        token = util.prompt_for_user_token(
            username=self.username,
            scope=self.scope,
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri)
        return token

    def get_song_uri(self, artist: str, song_name: str, access_token):
        q = f'artist:{artist} track:{song_name}'
        query = f'https://api.spotify.com/v1/search?q={q}&type=track&limit=1'

        response = requests.get(
            query,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
        )

        if not response.ok:
            return None

        results = response.json()
        items = results['tracks']['items']

        if not items:
            return None

        return items[0]['uri']#[14:]

    def create_playlist(self, playlist_name, playlist_description, access_token):

        request_body = {
            "name": playlist_name,
            "description": playlist_description,
            "public": True
        }

        query = f"https://api.spotify.com/v1/users/{'vv1q5k3gbuqcsoe3jcsdn17ha'}/playlists"

        response = requests.post(
            query,
            json=request_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}"
            }
        )

        playlist = response.json()
        return playlist['id']

    def add_song_to_playlist(self, song_uri, playlist_id, access_token):
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        response = requests.post(
            url,
            json={"uris": [song_uri]},
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        )
        return response

# sp = Spotify()
# token = sp.token
# id_of_playlist = sp.create_playlist()
# uri_of_song = sp.get_song_uri('Future', 'I Thank U')
# res = sp.add_song_to_playlist(uri_of_song, id_of_playlist)