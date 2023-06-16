# Importar as bibliotecas necessárias
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from sklearn.cluster import KMeans
from sklearn.neighbors import KNeighborsClassifier
import seaborn as sns
import numpy as np

# Definir as credenciais da API do spotify
client_id = '1e56a728a4c34fb79be646f9a7e2bb4e'
client_secret = '85d45ad9647d49d48819506ecf979641'
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)

sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Definir uma lista de géneros para pesquisar playlists
genres = ["rock","hip hop", "jazz", "classical", "pop"]


def func (song_id):
    # Criar um dataframe vazio para armazenar os dados das músicas e das playlists
    df = pd.DataFrame()
    # Para cada género, pesquisar 3 playlists e obter as músicas e os atributos de áudio de cada uma
    for genre in genres:
        print("Género: " + str(genre))
        # Pesquisar 3 playlists do género usando a API do spotify
        playlists = sp.search(q=genre, type="playlist", limit=3)

        # Para cada playlist, obter o id e o nome
        for playlist in playlists["playlists"]["items"]:
            playlist_id = playlist["id"]
            playlist_name = playlist["name"]
            print("Playlist: " + str(playlist_name))
            # Obter as músicas da playlist 
            tracks = sp.playlist_tracks(playlist_id)
            # Para cada música, obter o id, o nome, o artista e os seus atributos de áudio
            
            track_ids = []
            track_names = []
            track_artists = []
            for track in tracks["items"]:
                if track["track"] != None:###
                    track_id = track["track"]["id"]
                    track_name = track["track"]["name"]
                    track_artist = track["track"]["artists"][0]["name"]
                    if ((track_id not in track_ids) and (track_id != song_id)):
                        track_ids.append(track_id)
                        track_names.append(track_name)
                        track_artists.append(track_artist)

            track_features = sp.audio_features(track_ids)
            for i, track_id in enumerate(track_ids):
                track_data = {"track_id": track_id,
                            "track_name": track_names[i],
                            "track_artist": track_artists[i],
                            "genre": genre}
                # Adicionar os atributos de áudio ao dicionário
                track_data.update(track_features[i])
                track_df = pd.DataFrame(track_data, index=[0])
                # Adicionar o dicionário ao dataframe
                df = pd.concat([df, track_df], ignore_index=True)

    # Remover as colunas que não são necessárias para o modelo de machine learning
    df_kmeans = df.drop(columns=["type", "uri", "track_href", "analysis_url","track_id", "track_name", "track_artist", "genre","id"])
    corr_matrix = df_kmeans.corr()
    sns.heatmap(corr_matrix, vmin=-1, vmax=1, square=True, annot=True)
    sns.pairplot(df_kmeans)
    df_kmeans = df_kmeans.drop(columns=["duration_ms", "acousticness"])
    df_csv = pd.read_csv("spotify.csv",nrows=60000)
    df_csv.drop_duplicates(subset=['track_name',"track_artist"], keep="first", inplace=True)
    df_csv2 = df_csv.drop(columns=["track_artist","track_id","track_name","album_name","popularity","duration_ms","explicit","track_genre","Column1", "acousticness"])
    
    print("Missing values dos dados vindos do dataset:")
    print(df_csv2.isna().sum())
    #Juntar os dados todos
    df_kmeans = pd.concat([df_kmeans, df_csv2], ignore_index=True)

    print(df_kmeans.columns)
    print(df_kmeans["loudness"])
    print(df_kmeans["tempo"])
    print(df_kmeans["key"])
    print(df_kmeans["time_signature"])

    df_kmeans['loudness'] = (df_kmeans['loudness'] - df_kmeans['loudness'].min()) / (df_kmeans['loudness'].max() - df_kmeans['loudness'].min())
    df_kmeans['tempo'] = (df_kmeans['tempo'] - df_kmeans['tempo'].min()) / (df_kmeans['tempo'].max() - df_kmeans['tempo'].min())
    df_kmeans['key'] = (df_kmeans['key'] - df_kmeans['key'].min()) / (df_kmeans['key'].max() - df_kmeans['key'].min())
    df_kmeans['time_signature'] = (df_kmeans['time_signature'] - df_kmeans['time_signature'].min()) / (df_kmeans['time_signature'].max() - df_kmeans['time_signature'].min())

    print(df_kmeans["loudness"])
    print(df_kmeans["tempo"])
    print(df_kmeans["key"])
    print(df_kmeans["time_signature"])

    df_kmeans.to_csv("handledData.csv")

    if int(len(df_kmeans)/50) < 5:
        number_of_clusters = 5
    else:
        number_of_clusters = int(len(df_kmeans)/50)

    
    # Criar um modelo de machine learning usando o algoritmo K-means com k clusters
    model = KMeans(n_clusters=number_of_clusters, random_state=42)
    
    model.fit(df_kmeans)

    df_kmeans["cluster"] = model.labels_

    df = pd.concat([df,df_csv], ignore_index=True)
    df_concat = df.assign(cluster = df_kmeans["cluster"])

    return model, df_concat

# Definir uma função para fazer recomendações de músicas dado uma música como input
def recommend_songs(song):

    # Criar um dicionário com os atributos de áudio da música
    song_data = {}

    # Obter os atributos de áudio da música usando a API do spotify
    song_features = sp.audio_features(song)[0]
    song_data.update(song_features)

    model, df_concat = func(song_data['id'])
    
    # Remover os atributos que não são necessárias para o modelo de machine learning
    song_data.pop("type")
    song_data.pop("uri")
    song_data.pop("track_href")
    song_data.pop("analysis_url")
    song_data.pop("id")
    song_data.pop("duration_ms")
    song_data.pop("acousticness")

    # Transformar o dicionário num dataframe
    song_df = pd.DataFrame(song_data, index=[0])

    # Obter o label do cluster da música usando o modelo treinado
    song_cluster = model.predict(song_df)[0]
    # Filtrar o dataframe original para obter as músicas do mesmo cluster da música de input
    cluster_df = df_concat[df_concat["cluster"] == song_cluster]

    recommendations = cluster_df
    return list(recommendations.itertuples(index=False, name=None))

def main():
    
    song = "https://open.spotify.com/track/3yfqSUWxFvZELEM4PmlwIR?si=72e9e19aee5b4f25"
    # get track_id a partir da string fornecida em "song"
    parts = (song.split('/'))[-1].split('?')
    song_id = parts[0]
    recommendations = recommend_songs(song)
    print(recommendations)
    print(f"As recomendações para a música {song} são:")
    for rec in recommendations:
        print(f"- {rec[0]} - {rec[1]}")

    #generate html
    html_text="""<!DOCTYPE html>
      <html>
        <head>
          <title>Data Mining 23 - Spotify Secomendations</title>
        </head>
        <body>
          <h1>Se gostas desta música:</h1>
          <iframe style="border-radius:12px"
          src="https://open.spotify.com/embed/track/"""+song_id+"""?utm_source=generator" 
          width="100%" height="152" frameBorder="0" allowfullscreen="" allow="autoplay;
          clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
          <h1>Então experimenta estas: (a ordem é irrelevante)</h1>"""
    for rec in recommendations:
        html_text+="""
            <p><iframe style="border-radius:12px"
        src="https://open.spotify.com/embed/track/"""+rec[0]+"""?utm_source=generator"
        width="100%" height="152" frameBorder="0" allowfullscreen="" allow="autoplay;
        clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe></p>
            </body>
          </html>
        """

    with open('my_file.html', 'w') as f:
        # write the HTML string to the file
        f.write(html_text)

if __name__ == '__main__':
    main()
