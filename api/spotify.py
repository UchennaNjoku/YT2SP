from spotipy import util 
import requests
from os import getenv



class Spotify:

    def __init__(self):
        self.scope = 'playlist-modify-public'
        self.username = getenv('SPOTIPY_USER_ID')
        self.user_id = getenv('SPOTIPY_USER_ID')
        self.client_id = getenv('SPOTIPY_CLIENT_ID')
        self.client_secret = getenv('SPOTIPY_CLIENT_SECRET')
        self.redirect_uri = getenv('REDIRECT_URI')

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
