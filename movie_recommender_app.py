import streamlit as st
import joblib
import pandas as pd
import movieposters as mp
from concurrent.futures import ThreadPoolExecutor, as_completed

# -----------------------------
# Helper Functions
# -----------------------------

def fetch_posters(movie_names):
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(mp.get_poster, movie_name): movie_name for movie_name in movie_names}
        results = {}
        for future in as_completed(futures):
            movie_name = futures[future]
            try:
                results[movie_name] = future.result()
            except Exception:
                results[movie_name] = None
    return results

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    recommended_movies = [movies.iloc[i[0]].title for i in movies_list]
    
    with st.spinner('Fetching movie posters...'):
        posters = fetch_posters(recommended_movies)
    
    return recommended_movies, [posters.get(movie, None) for movie in recommended_movies]

# -----------------------------
# Load Data
# -----------------------------

movies_list = joblib.load('movies_dict.pkl')
movies = pd.DataFrame(movies_list)
similarity = joblib.load('similarity.pkl')

# -----------------------------
# Page Configuration
# -----------------------------

st.set_page_config(page_title="Movie Recommender", layout="wide")

# -----------------------------
# Custom CSS Styling
# -----------------------------

st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .title {
        text-align: center;
        font-size: 50px;
        font-weight: 700;
        color: #333;
        margin-bottom: 20px;
    }
    .footer {
        position: fixed;
        bottom: 10px;
        width: 100%;
        text-align: center;
        font-size: 13px;
        color: gray;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# App UI
# -----------------------------

st.markdown("<div class='title'>🎬 Movie Recommender System</div>", unsafe_allow_html=True)

selected_movie_name = st.selectbox('Search or select a movie:', movies['title'].values)

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)
    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            st.image(posters[i] if posters[i] else "https://via.placeholder.com/150?text=No+Poster", width=150)
            st.markdown(f"**{names[i]}**")

# -----------------------------
# Footer
# -----------------------------

st.markdown("<div class='footer'>Made with ❤️ using Streamlit</div>", unsafe_allow_html=True)
