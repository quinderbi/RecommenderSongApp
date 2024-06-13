import streamlit as st
import pandas as pd
import ast
from model import songs_recommendation, get_url

list_of_songs = [{'name': 'song1', 'artist':'artist1','duration_ms': 60000},{'name': 'song2', 'artist':'artist2','duration_ms': 2000},{'name': 'song3', 'artist':'artist3','duration_ms': 3000},{'name': 'song4', 'artist':'artist4','duration_ms': 4000},{'name': 'song5', 'artist':'artist5','duration_ms': 5000},{'name': 'song6', 'artist':'artist6','duration_ms': 6000},{'name': 'song7', 'artist':'artist7','duration_ms': 7000},{'name': 'song8', 'artist':'artist8','duration_ms': 8000},{'name': 'song9', 'artist':'artist9','duration_ms': 9000},{'name': 'song10', 'artist':'artist10','duration_ms': 10000}]

st.title('Music Recommender System')

st.header('Welcome to the Music Recommender System!')

st.write('This is a simple music recommender system that uses the Spotify API to recommend songs based on the song you input. The system uses the Spotify API to get the audio features of the song you input and then recommends songs that are similar to it.')

@st.cache_data()
def format_duration(duration_ms):
    return f'{str(duration_ms//60000).zfill(2)}:{str((duration_ms%60000)//1000).zfill(2)}'


df = pd.read_csv('data/data_clean.csv')
df['artists'] = df['artists'].apply(ast.literal_eval)

# 


with st.form(key='my_form'):
    song_title = st.text_input("Song title", "Love Story")
    button = st.form_submit_button("Generate")

if button:
    list_song_title = song_title.split(',')
    st.session_state.rs = songs_recommendation(list_song_title, df)

if "num_rec" not in st.session_state:
    st.session_state.num_rec = 10

if 'rs' not in st.session_state:
    st.session_state.rs = songs_recommendation(['Love Story'], df, st.session_state.num_rec)
    
with st.sidebar:

    with st.expander('⚙️ Setting'):
        num_rec = st.slider('Number of Recommendations', min_value=1, max_value=10, value=st.session_state.num_rec)

with st.spinner("Loading..."):
    st.write('Your Song')
    for song in st.session_state.rs[0]:
        col1, _ , col2, col3 = st.columns([0.1, 0.05, 0.35, 0.5])
        url = get_url(song['id'])
        col1.image(url["image"])
        col2.write(f"<b>{song["name"]}</b><br><span style='opacity: 0.75;'>\
            {song['artists'][0]} \u25cf {format_duration(song['duration_ms'])}</span>",\
            unsafe_allow_html=True)
        col3.audio(url['sample'], format='audio/ogg', start_time=0)
    st.write('Recommended Songs')
    for song in st.session_state.rs[1]:
        col1, _ , col2, col3 = st.columns([0.1, 0.05, 0.35, 0.5])
        url = get_url(song['id'])
        col1.image(url["image"])
        col2.write(f"<b>{song["name"]}</b><br><span style='opacity: 0.75;'>{song['artists'][0]} \u25cf {format_duration(song['duration_ms'])}</span>", unsafe_allow_html=True)
        col3.audio(url['sample'], format='audio/ogg', start_time=0)