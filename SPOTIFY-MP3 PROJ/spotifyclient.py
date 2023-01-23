import json

import requests

from track import Track
from playlist import Playlist

import eyed3
from tinytag import TinyTag as tt
import urllib
import os

class SpotifyClient:
    """SpotifyClient performs operations using the Spotify API."""

    def __init__(self, authorization_token, user_id):
        """
        :param authorization_token (str): Spotify API token
        :param user_id (str): Spotify user id
        """
        self._authorization_token = authorization_token
        self._user_id = user_id
        
        def __str__(self):
            return 'Client ' + self.user_id

    def get_last_played_tracks(self, limit=10):
        """Get the last n tracks played by a user

        :param limit (int): Number of tracks to get. Should be <= 50
        :return tracks (list of Track): List of last played tracks
        """
        url = f"https://api.spotify.com/v1/me/player/recently-played?limit={limit}"
        response = self._place_get_api_request(url)
        response_json = response.json()
        tracks = [Track(track["track"]["name"], track["track"]["id"], track["track"]["artists"][0]["name"]) for
                  track in response_json["items"]]
        return tracks

    def get_track_recommendations(self, seed_tracks, limit=50):
        """Get a list of recommended tracks starting from a number of seed tracks.

        :param seed_tracks (list of Track): Reference tracks to get recommendations. Should be 5 or less.
        :param limit (int): Number of recommended tracks to be returned
        :return tracks (list of Track): List of recommended tracks
        """
        seed_tracks_url = ""
        for seed_track in seed_tracks:
            seed_tracks_url += seed_track.id + ","
        seed_tracks_url = seed_tracks_url[:-1]
        url = f"https://api.spotify.com/v1/recommendations?seed_tracks={seed_tracks_url}&limit={limit}"
        response = self._place_get_api_request(url)
        response_json = response.json()
        tracks = [Track(track["name"], track["id"], track["artists"][0]["name"]) for
                  track in response_json["tracks"]]
        return tracks

    def create_playlist(self, name):
        """
        :param name (str): New playlist name
        :return playlist (Playlist): Newly created playlist
        """
        data = json.dumps({
            "name": name,
            "description": "Imported songs",
            "public": False
        })
        url = f"https://api.spotify.com/v1/users/{self._user_id}/playlists"
        response = self._place_post_api_request(url, data)
        response_json = response.json()
        # print(response_json)
        # create playlist
        playlist_id = response_json["id"]
        playlist = Playlist(name, playlist_id)
        return playlist

    def populate_playlist(self, playlist, tracks):
        """Add tracks to a playlist.

        :param playlist (Playlist): Playlist to which to add tracks
        :param tracks (list of Track): Tracks to be added to playlist
        :return response: API response
        """
        chunks = [tracks[x:x+100] for x in range(0, len(tracks), 100)]
        
        for split_tracks in chunks :
            
            track_uris = [track.create_spotify_uri() for track in split_tracks]
            data = json.dumps(track_uris)
            url = f"https://api.spotify.com/v1/playlists/{playlist.id}/tracks"
            response = self._place_post_api_request(url, data)
            response_json = response.json()
        return response_json

    def _place_get_api_request(self, url):
        response = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._authorization_token}"
            }
        )
        return response

    def _place_post_api_request(self, url, data):
        response = requests.post(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._authorization_token}"
            }
        )
        return response
    
    def _place_put_api_request(self, url, data):
        response = requests.put(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._authorization_token}"
            }
        )
        return response
    
    def files_finder(self, path, f=[]):
    
        for (dirpath, dirnames, filenames) in os.walk(path):
            
            break
        if len(filenames)>0:
            for file in filenames:
                
                f.append(dirpath + "\\" + file)
            
                
        
        if len(dirnames) != 0 :
            for dirname in dirnames:
                f = self.files_finder(dirpath + '\\' + dirname,f)
                
        return f
        
        
    def filter_files(self, files):
        #music files only filter
        music_files = []
        
        for i in range (len(files)):
            if files[i][-4:] in ['.mp3', '.m4a', '.wma','.wav','flac'] :
                music_files.append(files[i])
        return music_files

    
    def create_tracks(self,tracks,path):
        
        TRACKS = []
        for track in tracks:
            tag = tt.get(track)
            title = tag.title
            
            artist = tag.artist
            album = tag.album
            
            if title != None and artist != None:
                if '(' in title:
                    title = title[:title.index('(')]
                elif '[' in title:
                    title = title[:title.index('[')]
                    
                elif 'feat' in title:
                    title = title[:title.index('feat')]
                
                elif '(ft.' in title:
                    title = title[:title.index('ft.')]
                    
                TRACKS.append(Track(title,artist,album))
        
        return TRACKS
            
    def search_tracks(self,tracks, manual_selection):
        final_tracks = []
        match = 0
        for track in tracks:
            # print(track)
            url = f"https://api.spotify.com/v1/search?q={urllib.parse.quote(track.name)}&type=track&market=FR&limit=10"
            response = self._place_get_api_request(url)
            if 'error' in response:
                print (response)
            response_json = response.json()
            if 'tracks' in response_json:
            
                result_tracks = [Track(track["name"], track["artists"][0]["name"], track['album']['name'], track["id"]) for track in response_json["tracks"]["items"]]
                # print(result_tracks)
                if track in result_tracks:
                    track.id = result_tracks[result_tracks.index(track)].id
                    # print(track.id)
                    final_tracks.append(track)
                    match += 1
                    
                else :
                    url = f"https://api.spotify.com/v1/search?q={urllib.parse.quote(track.name+' '+track.artist)}&type=track&market=FR&limit=10"
                    response = self._place_get_api_request(url)
                    if 'error' in response:
                        print (response)
                    response_json = response.json()
                    if 'tracks' in response_json:
                    
                        result_tracks2 = [Track(track["name"], track["artists"][0]["name"], track['album']['name'], track["id"]) for track in response_json["tracks"]["items"]]
                        if track in result_tracks2:
                            track.id = result_tracks2[result_tracks2.index(track)].id
                            # print(track.id)
                            final_tracks.append(track)
                            match += 1
                        elif manual_selection :
                            ans = ''
                            if len(result_tracks2)>0:
                                print('\n','Your track : ',track)
                                print(f"\nHere are the {len(result_tracks2)} tracks found on Spotify:")
                                for index, track in enumerate(result_tracks2):
                                    print(f"{index+1}- {track}")
                                    
                                ans = input('Pick your track or press "n" to see more results')
                            if ans == 'n' or len(result_tracks2) == 0:
                                if len(result_tracks)>0:
                                    print('\n','Your track : ',track)
                                    print(f"\nHere are the {len(result_tracks)} tracks found on Spotify:")
                                    for index, track in enumerate(result_tracks):
                                        print(f"{index+1}- {track}")
                                        
                                    ans = input('Pick your track or press "n" to skip')
                                    
                                    if ans != 'n':
                                        try :
                                             track.id = result_tracks[int(ans)-1].id
                                            # print(track.id)
                                             final_tracks.append(track)
                                             match += 1
                                        except IndexError or ValueError:
                                            print('Wrong number')
                                else :
                                    print('No match found for ', track)
                                        
                            else :
                                try :
                                    track.id = result_tracks2[int(ans)-1].id
                                    # print(track.id)
                                    final_tracks.append(track)
                                    match += 1
                                except IndexError or ValueError:
                                     print('Wrong number')
                                    
                            
                # print('y')
        print('Number of tracks found in Spotify :',match)
        
        return final_tracks
    
    def play_playlist(self, playlist,device):
        playlist_uris = "spotify:playlist:" + playlist
        data = json.dumps({'context_uri':playlist_uris})
        
        device_id = device['id']
        url = f"https://api.spotify.com/v1/me/player/play?device_id={device_id}"
        response = self._place_put_api_request(url, data)
        
        
        
    
    def get_available_devices(self):
        url = "https://api.spotify.com/v1/me/player/devices"
        response = self._place_get_api_request(url)
        response_json = response.json()
        
        devices = [device for   device in response_json["devices"]]
        
        # print("\nHere are the available devices:")
        # for index, device in enumerate(devices):
        #     print(f"{index+1}- {device['name']}")
        
        
        return devices
    
    def get_playlist_image(self, playlist):
    
        url = f"https://api.spotify.com/v1/playlists/{playlist}/images"
        response = self._place_get_api_request(url)
        return response['url']
        
        
        
            
        