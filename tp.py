import spotipy
from spotipy import oauth2
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
from tokens import client_token, secret_token
import spotipy.util as util
import json

# gets all songs from the playlists, grouped by owner of playlist
def getSongsFromPlaylist(spotify, list_of_playlists):

    res = {}

    for playlist in list_of_playlists:

        results = spotify.playlist(playlist)
        """
        owner_id = results['owner']['id']
        #create user in outter dictionary
        if owner_id not in res:
            res[owner_id] = {}

        #create playlist_id on inner dictionary
        if playlist not in res[owner_id]:
            res[owner_id][playlist] = []"""

        if playlist not in res:
            res[playlist] = []

        for item in results['tracks']['items']:
            song_id = item['track']['id']
            #res[owner_id][playlist].append(song_id)
            res[playlist].append(song_id)

    return res

def main():
    spotify = spotipy.Spotify(
        client_credentials_manager=SpotifyClientCredentials(client_id=client_token, client_secret=secret_token))

    list_of_playlists = ['3YjyB3anOIsK7qw8cdUeV4','0wSuXtjnRL4Gzyqjbi39jd']

    res = getSongsFromPlaylist(spotify, list_of_playlists)
    print(res)



if __name__ == '__main__':
    main()

