import joblib
import pandas as pd
import numpy as np
import ast
from scipy.spatial.distance import cdist



import yaml
import spotipy
from spotipy.oauth2 import SpotifyOAuth,SpotifyClientCredentials

DF_COLUMNS = ['valence', 'year', 'acousticness', 'artists', 'danceability',
       'duration_ms', 'energy', 'id', 'instrumentalness', 'key',
       'liveness', 'loudness', 'mode', 'name', 'popularity', 'release_date',
       'speechiness', 'tempo']
DF_COLUMNS_MODEL = ['valence', 'year', 'acousticness','artists', 'danceability',
         'duration_ms', 'energy', 'instrumentalness', 'key',
         'liveness', 'loudness', 'mode', 'popularity', 'speechiness', 'tempo']

pipeline = joblib.load('model/pipeline.pkl')


stream= open("streamlit/spotify/spotify.yaml")
spotify_details = yaml.safe_load(stream)
auth_manager = SpotifyClientCredentials(client_id=spotify_details['Client_id'],
                                        client_secret=spotify_details['client_secret'])

sp = spotipy.client.Spotify(auth_manager=auth_manager)

def get_song_spotify(song_name, data):
    log = open('log.txt','w')
    try:
        result = sp.search(q=song_name, limit=1)
    except:
        log.write('Error: Failed to search song')
        return None

    if result['tracks']['items'] == []:
        return None

    song = result['tracks']['items'][0]

    id = song['id']

    try:
        song_data = data[(data['id'] == id)].iloc[0]
        return song_data
    except:
        try:
            audio_features = sp.audio_features(id)
            song_data = {
                'valence': audio_features[0]['valence'],
                "year" : result['tracks']['items'][0]['album']['release_date'][:4],
                'acousticness': audio_features[0]['acousticness'],
                'artists': list(map(lambda x: x['name'], result['tracks']['items'][0]['artists'])),
                'danceability': audio_features[0]['danceability'],
                'duration_ms': audio_features[0]['duration_ms'],
                'energy': audio_features[0]['energy'],
                'id': id,
                'instrumentalness': audio_features[0]['instrumentalness'],
                'key': audio_features[0]['key'],
                'liveness': audio_features[0]['liveness'],
                'loudness': audio_features[0]['loudness'],
                'mode': audio_features[0]['mode'],
                'name': result['tracks']['items'][0]['name'],
                'popularity': result['tracks']['items'][0]['popularity'],
                'speechiness': audio_features[0]['speechiness'],
                'tempo': audio_features[0]['tempo']
            }
        except:
            log.write('Error: Failed to get audio features from Spotify')
            return None

        return pd.DataFrame([song_data], columns=DF_COLUMNS).iloc[0]

def get_song_data(song_name, data):
    try:
        song_data = data[(data['name'] == song_name)].iloc[0]
        return song_data
    except:
        return get_song_spotify(song_name,data)

def df_song_data(list_song_name,data):
    rows_song_data = list()
    for song_name in list_song_name:
        rows_song_data.append(get_song_data(song_name,data))

    return pd.DataFrame(rows_song_data,columns=DF_COLUMNS)

def songs_recommendation(list_song_name,data,num_rec=10):

    song_data_input = df_song_data(list_song_name,data).to_dict(orient='records')

    vector = pipeline.named_steps["preprocessor"].transform(df_song_data(list_song_name,data))
    vector = pipeline.named_steps["scaler"].transform(vector)

    vector = vector.mean(axis=0)

    predicted_cluster = pipeline.named_steps["kmeans"].predict([vector])

    cluster_data = data[pipeline.named_steps["kmeans"].labels_ == predicted_cluster[0]]

    vector_cluster = pipeline.named_steps["preprocessor"].transform(cluster_data)
    vector_cluster = pipeline.named_steps["scaler"].transform(vector_cluster)

    distance = cdist([vector],vector_cluster)
    index = list(np.argsort(distance)[:, :num_rec][0])

    recsongs = cluster_data.iloc[index]
    recsongs = recsongs[~recsongs['name'].isin(list_song_name)].to_dict(orient='records')
    return song_data_input,recsongs

def get_url(id_track):
    try:
        result = sp.track(id_track)
        return {"image": result['album']['images'][0]['url'],"sample": result['preview_url']}
    except:
        return 'https://i.scdn.co/image/ab67616d00004851f221ae4798e902bf102e1bd2'


df = pd.read_csv('data/data_clean.csv')
df['artists'] = df['artists'].apply(ast.literal_eval)

