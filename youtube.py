from googleapiclient.discovery import build
from youtube_title_parse import get_artist_title
from dataclasses import dataclass
import re
from pprint import pprint
from os import getenv
from dotenv import load_dotenv

@dataclass
class Song: # dataclass to create objects for each song
    artist: str
    title: str

class Youtube:

    load_dotenv()

    def clean_song_info(self, song: Song) -> Song:
        artist, title = song.artist, song.title
        title = re.sub('\(.*', '', title)          # Remove everything after '(' including '('
        title = re.sub('ft.*', '', title)          # Remove everything after 'ft' including 'ft'
        title = re.sub(',.*', '', title)           # Remove everything after ',' including ','
        artist = re.sub('\sx\s.*', '', artist)     # Remove everything after ' x ' including ' x '
        artist = re.sub('\(.*', '', artist)        # Remove everything after '(' including '('
        artist = re.sub('ft.*', '', artist)        # Remove everything after 'ft' including 'ft'
        artist = re.sub(',.*', '', artist)         # Remove everything after ',' including ','
        return Song(artist.strip(), title.strip()) # Remove whitespaces from start and end


    def get_playlist_id(self, url):
        # This regex looks for a 'list=' parameter and captures the ID that follows
        match = re.search(r"list=([a-zA-Z0-9_-]+)", url)
        if match:
            return match.group(1)
        else:
            raise ValueError("Could not extract playlist ID from URL")



    def get_playlist_response(self, playlist_identification):

        #  queries the youtube api for playlist items
        youtube_api_key = getenv('YOUTUBE_DEVELOPER_KEY', None)
        youtube = build('youtube', 'v3', developerKey=youtube_api_key)
        request = youtube.playlistItems().list(
        part = 'snippet',  playlistId = playlist_identification,
            maxResults = 50).execute()
        return request
    # playlist_identification = get_playlist_id('self')
    # youtube_response = get_playlist_response('self', playlist_identification)
    # playlist_songs = []

    def list_playlist_songs(self):
        for i in range(len(self.youtube_response['items'])):
            self.playlist_songs.append(self.youtube_response['items'][i]['snippet']['title'])

        return self.playlist_songs


# yt = Youtube()
# yt.list_playlist_songs()

# parsed_songs = []
# def parse_em():
#     for item in yt.playlist_songs:
#         try:
#             artist, title = get_artist_title(item)
#             parsed_songs.append(yt.clean_song_info(Song(artist, title)))
#         except:
#             pass
# parse_em()
# pprint(parsed_songs)