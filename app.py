#UPDATES FOR TOMORROW WORK ON SHOWING THE USER WHATS HAPPENING AS WELL AS HAVING A USER-AUTH PAGE AND CSS-STYLING 

from flask import Flask, render_template, request
from spotify import Spotify
from youtube import Youtube, Song
from pprint import pprint
from youtube_title_parse import get_artist_title


app = Flask(__name__)
sp = Spotify()
yt = Youtube()

@app.route("/", methods = ['POST', 'GET'])
def home():
    if request.method == 'POST':

        yt_url = request.form['yt_url']
        sp_playlist_name = request.form['sp_playlist_name']
        sp_playlist_description = request.form['sp_playlist_description']

        # fetch songs from youtube playlist, given url
        playlist_identification = yt.get_playlist_id(yt_url)
        youtube_response = yt.get_playlist_response(playlist_identification)

        # appending each song to a playlist list
        playlist_songs = []
        for i in range(len(youtube_response['items'])):
            playlist_songs.append(youtube_response['items'][i]['snippet']['title'])

        # parsing the list of song objects into searchable artist and song titles
        parsed_songs = []
        for item in playlist_songs:
            try:
                artist, title = get_artist_title(item)
                parsed_songs.append(yt.clean_song_info(Song(artist, title)))
            except:
                pass

        # create empty playlist in spotify
        id_of_playlist = sp.create_playlist(sp_playlist_name, sp_playlist_description)

        # iterate through parsed songs and each to the empty playlist first finding uri then adding

        for song in parsed_songs:

            # getting the uri of each song
            uri_of_song = sp.get_song_uri(song.artist, song.title)
            if not uri_of_song:
                # print(f"{song.artist} - {song.title} was not found!")
                continue

            was_added = sp.add_song_to_playlist(uri_of_song, id_of_playlist)

            #if was_added:
            #    print(f'{song.artist} - {song.title} was added to playlist.')
        return render_template("index.html")
        
    else:
        return render_template("index.html") 


if __name__ == "__main__":
    app.run(debug=True)
