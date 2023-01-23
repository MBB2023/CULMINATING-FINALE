import os
import playlist as pl

from spotifyclient import SpotifyClient



 



            
    
        
def main(path, authorization_token, user_id, playlist_name):        

    f =[]
    
    def files_finder(path):
    
        for (dirpath, dirnames, filenames) in os.walk(path):
            
            break
        if len(filenames)>0:
            for file in filenames:
                
                f.append(dirpath + "\\" + file)
            
                
        
        if len(dirnames) != 0 :
            for dirname in dirnames:
                files_finder(dirpath + '\\' + dirname)
    
    files_finder(path)
        
    print('Number of files found : '+ str(len(f)))
    
    
    #music files only filter
    music_files = []
    
    for i in range (len(f)):
        if f[i][-4:] in ['.mp3', '.m4a', '.wma','.wav','flac'] :
            music_files.append(f[i])
    
    
        
            
    print('Number of tracks found in the directory: '+ str(len(music_files)))


    spotify_client = SpotifyClient(authorization_token,
                                   user_id)



    # get playlist name from user and create playlist
    
    playlist = spotify_client.create_playlist(playlist_name)
    print(f"\nPlaylist '{playlist.name}' was created successfully.")
    
    tracks = spotify_client.create_tracks(music_files,path)
    
    print('Number of tracks with good metadata: '+ str(len(tracks)))
    
    
    ans = input('Would you like to manually select tracks which doesnt match ? (y/n)')
    
    if ans == 'y':
        manual_selection = True
        
    else :
        manual_selection = False 
    
    
    
    found_tracks = spotify_client.search_tracks(tracks, manual_selection)
   
          
    # populate playlist with recommended tracks
    response = spotify_client.populate_playlist(playlist, found_tracks)
    
    print(f"\nYour tracks successfully uploaded to playlist '{playlist.name}'.")
    
    # playlist = pl.Playlist('test', '2o5jtsdipiidfsYQ2dnv6p')
    
    
    ans = input('Would you like to start the playlist ? (y/n)')
    
    if ans == 'y':
         spotify_client.play_playlist(playlist)
    
    return tracks,found_tracks


