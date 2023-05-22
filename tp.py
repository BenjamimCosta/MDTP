import spotipy
import csv
from fpgrowth_py import fpgrowth
from spotipy.oauth2 import SpotifyClientCredentials
from tokens import client_token, secret_token


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
            # res[owner_id][playlist].append(song_id)
            res[playlist].append(song_id)

    return res


def main():
    # initiate spotify client
    spotify = spotipy.Spotify(
        client_credentials_manager=SpotifyClientCredentials(client_id=client_token, client_secret=secret_token))

    # input here the playlist ids
    # list_of_playlists = ['3YjyB3anOIsK7qw8cdUeV4','0wSuXtjnRL4Gzyqjbi39jd']
    list_of_playlists = ['0hO6tRnbeCUU6IGjlMxcut', '2CuIyKHyAKKqA9ruLOOUop', '53Ykpk4dim5I6LAMG7Ayk8']

    # result from all the playlists
    res = getSongsFromPlaylist(spotify, list_of_playlists)

    # writing to csv
    with open('output.csv', 'w', newline='') as f:
        writer = csv.writer(f, lineterminator='\n')
        for value in res.values():
            writer.writerow(value)

    itemSetList = []

    # getting from csv (will be useful if we dont use api in the future)
    with open('output.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            itemSetList.append(row)

    freqItemSet, rules = fpgrowth(itemSetList, minSupRatio=0.5, minConf=0.5)
    print(freqItemSet)
    print(rules)


if __name__ == '__main__':
    main()
