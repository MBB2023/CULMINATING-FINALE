import spotipy #python based spotify API library
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, url_for, session, request, redirect, render_template
import json
import time
import pandas as pd
import spotifyclient
from  spotifyclient import SpotifyClient
# from .downloadvideos import DownloadVideosFromTitles

# App config
app = Flask(__name__)


app.secret_key = '84b8bbf6f849474cb47212cc5d7911e6'
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'



@app.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    
    return redirect(auth_url)

@app.route('/authorize')
def authorize():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    session["path"] = 'a'
    return redirect("/PlaylistName")

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')



@app.route('/PlaylistName')
def my_form():
    return render_template('my-form.html')

@app.route('/PlaylistName', methods=['POST'])
def my_form_post():
    
    playlist_name = request.form['playlist']
    path = request.form['path']
    
    # manual_selection = request.form.get('manual_selection')
    # manual_selection = manual_selection == 'on'
    
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    user_id = sp.me()['id']
    authorization_token = session['token_info']['access_token']
    
    
    spotify_client = SpotifyClient(authorization_token, user_id)
    
    files = spotify_client.files_finder(path)
    music_files = spotify_client.filter_files(files)
    
    tracks = spotify_client.create_tracks(music_files,path)
    
    found_tracks = spotify_client.search_tracks(tracks, False)
   
    playlist = spotify_client.create_playlist(playlist_name)      
    # populate playlist with recommended tracks
    response = spotify_client.populate_playlist(playlist, found_tracks)
    
    print(f"\nYour tracks successfully uploaded to playlist '{playlist.name}'.")
    
    # playlist = pl.Playlist('test', '2o5jtsdipiidfsYQ2dnv6p')
    
    
    
    
    return (redirect(url_for('play', playlist_id=playlist.id, name = playlist_name, number=len(found_tracks) )))
    
@app.route('/Play/<number>/<name>/<playlist_id>')
def play(playlist_id, name, number):
    
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    user_id = sp.me()['id']
    authorization_token = session['token_info']['access_token']
    
    
    spotify_client = SpotifyClient(authorization_token, user_id)
    
    
    devices = spotify_client.get_available_devices()
    devices_names = [ device['name'] for device in devices]
    
    return render_template("playlist-options.html", playlist_id=playlist_id, name = name, number=number, devices= devices_names, devices_number=len(devices_names) ) 

@app.route('/Play/<number>/<name>/<playlist_id>', methods=['POST'])
def play_post(playlist_id, name, number): 
    
    if request.form.get('reset') != None :
        return redirect('/') 
    
    else :
    
        session['token_info'], authorized = get_token()
        session.modified = True
        if not authorized:
            return redirect('/')
        sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
        user_id = sp.me()['id']
        authorization_token = session['token_info']['access_token']
        
        
        spotify_client = SpotifyClient(authorization_token, user_id)
        
        
        devices = spotify_client.get_available_devices()
        
        device_number=0
        
            
        for i in range(len(devices)):
            if request.form.get(f'button{i}') == f"button{i}":
            
                device_number=i
            
        
        spotify_client.play_playlist(playlist_id
                                     , devices[device_number])
        
        
        return redirect(f'/Play/{number}/{name}/{playlist_id}')
        




@app.route('/getTracks')
def get_all_tracks():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    user_id = sp.me()['id']
    authorization_token = session['token_info']['access_token']
    
    
    spotify_client = SpotifyClient(authorization_token, user_id)
    # results = []
    # iter = 0
    # while True:
    #     offset = iter * 50
    #     iter += 1
    #     curGroup = sp.current_user_saved_tracks(limit=50, offset=offset)['items']
    #     for idx, item in enumerate(curGroup):
    #         track = item['track']
    #         val = track['name'] + " - " + track['artists'][0]['name']
    #         results += [val]
    #     if (len(curGroup) < 50):
    #         break
    
    # df = pd.DataFrame(results, columns=["song names"]) 
    # df.to_csv('songs.csv', index=False)
    return "done"


# Checks to see if token is valid and gets a new token if not
def get_token():
    token_valid = False
    token_info = session.get("token_info", {})

    # Checking if the session already has a token stored
    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    # Refreshing token if it has expired
    if (is_token_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid


def create_spotify_oauth():
    return SpotifyOAuth(
            client_id="22a19ef0094246f084f2f115e3ca70e5",
            client_secret="84b8bbf6f849474cb47212cc5d7911e6",
            redirect_uri=url_for('authorize', _external=True),
            scope="user-modify-playback-state playlist-modify-private playlist-modify-public user-read-playback-state") # Where we ask spotify for what we want

if __name__ == "__main__":
    app.run()