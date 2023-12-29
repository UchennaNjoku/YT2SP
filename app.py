from flask import Flask, render_template, redirect, request, make_response, session, redirect, url_for, jsonify
from spotify import Spotify
from youtube import Youtube, Song
from pprint import pprint
from youtube_title_parse import get_artist_title
from os import getenv
from dotenv import load_dotenv
import requests
import time
from flask_cors import CORS



load_dotenv()
app = Flask(__name__)
app.secret_key="sessionkey"

CORS(app)

sp = Spotify()
yt = Youtube()

API_BASE = 'https://accounts.spotify.com'
REDIRECT_URI = "http://127.0.0.1:5000/api_callback"
SCOPE = 'playlist-modify-public'
SHOW_DIALOG = True

CLIENT_ID = getenv('SPOTIPY_CLIENT_ID', None)
CLIENT_SECRET = getenv('SPOTIPY_CLIENT_SECRET', None)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login" , methods=['POST', 'GET'])
def verify():
    auth_url = f'{API_BASE}/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={SCOPE}&show_dialog={SHOW_DIALOG}'
    return redirect(auth_url)


@app.route("/form", methods=['POST', 'GET'])
def form():
    return render_template("form.html")


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
    try:
        print(request.form)
        
        sp_playlist_name = request.form['sp_playlist_name']
        sp_playlist_description = request.form['sp_playlist_description']
        yt_url = request.form['yt_url']
        
        access_token = session.get('toke')
        
        if not access_token:
            return jsonify({'success': False, 'error': 'Missing access token.'}), 403
        
        id_of_playlist = sp.create_playlist(sp_playlist_name, sp_playlist_description, access_token)
        
        playlist_identification = yt.get_playlist_id(yt_url)
        youtube_response = yt.get_playlist_response(playlist_identification)
        
        playlist_songs = []
        for i in range(len(youtube_response['items'])):
            playlist_songs.append(youtube_response['items'][i]['snippet']['title'])
        
        parsed_songs = []
        for item in playlist_songs:
            try:
                artist, title = get_artist_title(item)
                parsed_songs.append(yt.clean_song_info(Song(artist, title)))
            except:
                pass

        for song in parsed_songs:
            uri_of_song = sp.get_song_uri(song.artist, song.title, access_token)
            if uri_of_song:
                sp.add_song_to_playlist(uri_of_song, id_of_playlist, access_token)

        return jsonify({'success': True})
    
    except Exception as e:
        print(e)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/success', methods=['GET', 'POST'])        
def success():
    return render_template('success.html')

@app.route('/about', methods=['GET', 'POST'])        
def about():
    return render_template('about.html')

if __name__ == "__main__":
    app.run(debug=True)
