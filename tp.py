import spotipy
import csv
from spotipy import oauth2
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
from tokens import client_token, secret_token
import spotipy.util as util
import json


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

    # initiate spotify client
    spotify = spotipy.Spotify(
        client_credentials_manager=SpotifyClientCredentials(client_id=client_token, client_secret=secret_token))

    # input here the playlist ids
    list_of_playlists = ['3YjyB3anOIsK7qw8cdUeV4','0wSuXtjnRL4Gzyqjbi39jd']

    # result from all the playlists
    res = getSongsFromPlaylist(spotify, list_of_playlists)

    # writing to csv
    with open('output.csv', 'w', newline='') as f:
        writer = csv.writer(f, lineterminator='\n')
        for value in res.values():
            writer.writerow(value)

    # call here fptree method


if __name__ == '__main__':
    main()

