from flask import Flask, render_template, redirect, request, make_response, session, redirect, url_for
from spotify import Spotify
from youtube import Youtube, Song
from pprint import pprint
from youtube_title_parse import get_artist_title
from os import getenv
from dotenv import load_dotenv
import requests
import time


load_dotenv()
app = Flask(__name__)
app.secret_key="xyz"

sp = Spotify()
yt = Youtube()

API_BASE = 'https://accounts.spotify.com'
REDIRECT_URI = "http://127.0.0.1:5000/api_callback"
SCOPE = 'playlist-modify-public'
SHOW_DIALOG = True

CLIENT_ID = getenv('SPOTIPY_CLIENT_ID', None)
CLIENT_SECRET = getenv('SPOTIPY_CLIENT_SECRET', None)


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template("home.html")


# authorization-code-flow Step 1. Have your application request authorization; 
# the user logs in and authorizes access
'''UNCOMMENT THE APP ROUTE WITH A LOGIN ROUTE INSTEAD'''
@app.route("/login" , methods=['POST', 'GET'])
def verify():
    auth_url = f'{API_BASE}/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={SCOPE}&show_dialog={SHOW_DIALOG}'
    print(auth_url)
    return redirect(auth_url)


@app.route("/form", methods=['POST', 'GET'])
def form():
    return render_template("form.html")

# authorization-code-flow Step 2.
# Have your application request refresh and access tokens;
# Spotify returns access and refresh tokens
@app.route("/api_callback")
def api_callback():
    session.clear()
    code = request.args.get('code')

    auth_token_url = f"{API_BASE}/api/token"
    res = requests.post(auth_token_url, data={
        "grant_type":"authorization_code",
        "code":code,
        "redirect_uri":"http://127.0.0.1:5000/api_callback",
        "client_id":CLIENT_ID,
        "client_secret":CLIENT_SECRET
        })

    res_body = res.json()
    print(res.json())
    session["toke"] = res_body.get("access_token")

    return redirect("form")

@app.route("/go", methods=['POST'])
def go():

    # GET THE VARIABLES FROM FORM
    sp_playlist_name = request.form['sp_playlist_name']
    sp_playlist_description = request.form['sp_playlist_description']
    yt_url = request.form['yt_url']

    # SPOTIFY ACCESS TOKEN FROM SESSION
    access_token = session['toke']

    # CREATE EMPTY SPOTIFY PLAYLIST
    id_of_playlist = sp.create_playlist(sp_playlist_name, sp_playlist_description, access_token)

    # FETCH THE SONGS IN YOUTUBE PLAYLIST USING THE URL FROM FORM
    playlist_identification = yt.get_playlist_id(yt_url)
    youtube_response = yt.get_playlist_response(playlist_identification)

    # CREATE AN EMPTY LIST AND APPEND EACH SONG FROM ^^ TO THE LIST
    playlist_songs = []
    for i in range(len(youtube_response['items'])):
        playlist_songs.append(youtube_response['items'][i]['snippet']['title'])

    # CONVERT EACH SONG IN THE LIST INTO A PARSED SEARCHABLE FORMAT TO BE USED BY SPOTIFY
    parsed_songs = []
    for item in playlist_songs:
        try:
            artist, title = get_artist_title(item)
            parsed_songs.append(yt.clean_song_info(Song(artist, title)))
        except:
            pass

    # ITERATE THROUGH PARSED SONGS; ADD TO EMPTY SPOTIFY PLAYLIST 
    for song in parsed_songs:

        # getting the uri of each song
        uri_of_song = sp.get_song_uri(song.artist, song.title, access_token)
        if not uri_of_song:
            # print(f"{song.artist} - {song.title} was not found!")
            continue

        was_added = sp.add_song_to_playlist(uri_of_song, id_of_playlist, access_token)
        #if was_added:
            #    print(f'{song.artist} - {song.title} was added to playlist.')


    return render_template("success.html")


@app.route('/success', methods=['GET', 'POST'])        
def success():
    return render_template('success.html')

if __name__ == "__main__":
    app.run(debug=True)
