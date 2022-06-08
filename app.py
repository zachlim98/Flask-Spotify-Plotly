"""
Prerequisites
    pip3 install spotipy Flask Flask-Session
    // from your [app settings](https://developer.spotify.com/dashboard/applications)
    export SPOTIPY_CLIENT_ID=client_id_here
    export SPOTIPY_CLIENT_SECRET=client_secret_here
    export SPOTIPY_REDIRECT_URI='http://127.0.0.1:8080' // must contain a port
    // SPOTIPY_REDIRECT_URI must be added to your [app settings](https://developer.spotify.com/dashboard/applications)
    OPTIONAL
    // in development environment for debug output
    export FLASK_ENV=development
    // so that you can invoke the app outside of the file's directory include
    export FLASK_APP=/path/to/spotipy/examples/app.py
 
    // on Windows, use `SET` instead of `export`
Run app.py
    python3 app.py OR python3 -m flask run
    NOTE: If receiving "port already in use" error, try other ports: 5000, 8090, 8888, etc...
        (will need to be updated in your Spotify app and SPOTIPY_REDIRECT_URI variable)
"""

import os
import json
from flask import Flask, session, request, redirect, render_template
from flask_session import Session
import spotipy
import uuid

import pandas as pd
import plotly
import plotly.express as px

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

caches_folder = '.spotify_caches'
# if not os.path.exists(caches_folder):
#     os.makedirs(caches_folder)

def session_cache_path():
    return caches_folder + session.get('uuid')

@app.route('/')
def index():
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing playlist-modify-private',
                                                cache_handler=cache_handler, 
                                                show_dialog=True)

    if request.args.get("code"):
        # Step 3. Being redirected from Spotify auth page
        aut_code = auth_manager.get_access_token(request.args.get("code"))
        session["token"] = auth_manager.get_access_token(aut_code)["access_token"]
        return redirect('/logged')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return f'<h2><a href="{auth_url}">Sign in</a></h2>'

@app.route('/logged')
def display_page():
    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth = session["token"])
    return f'<h2>Hi {spotify.me()["display_name"]}, ' \
        f'<small><a href="/sign_out">[sign out]<a/></small></h2>' \
        f'<a href="/artist_route">Top Artists</a> | ' \
        f'<a href="/current_user">me</a>' \

@app.route('/sign_out')
def sign_out():
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(caches_folder)
        session.clear()
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/')


@app.route('/artist_route')
def artist_route():
    return f'<h2>Please choose the duration history that you would like to see </h2>' \
        f'<a href="/long_term">Literally since you created a Spotify account</a> | ' \
        f'<a href="/mid_term">Last 6 months</a> |' \
        f'<a href="/short_term">Last 4 weeks</a> |' \


@app.route('/long_term')
def long_term():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/')
    spotify = spotipy.Spotify(auth = session["token"])
    track = spotify.current_user_playing_track()
    if not track is None:
        return track
    return "No track currently playing."


@app.route('/short_term')
def short_term():
    # cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    # auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    # if not auth_manager.validate_token(cache_handler.get_cached_token()):
    #     return redirect('/')
    spotify = spotipy.Spotify(auth = session["token"])

    st = spotify.current_user_top_artists(time_range="short_term")

    name = []
    popularity =[]

    for i in st["items"]:
        name.append(i["name"])
        popularity.append(i["popularity"])

    df = pd.DataFrame({"Name" : name, "Popularity" : popularity})

    fig = px.pie(df, values = "Popularity", names="Name")

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('short_term.html', graphJSON=graphJSON)


'''
Following lines allow application to be run more conveniently with
`python app.py` (Make sure you're using python3)
(Also includes directive to leverage pythons threading capacity.)
'''
if __name__ == '__main__':
    app.run(threaded=True, port=int(os.environ.get("PORT",
                                                   os.environ.get("SPOTIPY_REDIRECT_URI", 8080).split(":")[-1])))