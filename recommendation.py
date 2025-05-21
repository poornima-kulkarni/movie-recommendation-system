import streamlit as st
import joblib
import requests
import time

# ✅ Updated fetch_poster with headers, timeout, and error handling
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {
        "api_key": "55fe9c3ae3ab375e35137377c11e42de",
        "language": "en-US"
    }
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if 'poster_path' in data and data['poster_path']:
            return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
        else:
            return "https://via.placeholder.com/300x450?text=No+Image"
    except requests.exceptions.RequestException as e:
        print(f"Error fetching poster for movie ID {movie_id}: {e}")
        return "https://via.placeholder.com/300x450?text=No+Image"

# ✅ Updated get_movie_id with headers, timeout, and error handling
def get_movie_id(movie_name):
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": "55fe9c3ae3ab375e35137377c11e42de",
        "query": movie_name
    }
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data["results"]:
            return data["results"][0]["id"]
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching movie ID for '{movie_name}': {e}")
        return None

# 🧠 Session State
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# 🏠 Home Page
def home():
    st.title("🎬 Movie Recommender")
    st.write("Dive into a world of movies! Choose your preferred cinema.")
    st.markdown("---")
    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.subheader("Select Movie Genre")
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Bollywood", use_container_width=True):
                st.session_state.page = 'bollywood'
                st.rerun()
        with col_btn2:
            if st.button("Hollywood", use_container_width=True):
                st.session_state.page = 'hollywood'
                st.rerun()
    st.markdown("---")

# 🎥 Bollywood Page
def bollywood_page():
    st.title("🎥 Bollywood Movie Recommender")
    st.markdown("*Find your next favorite Bollywood flick!*")
    st.markdown("---")

    df = joblib.load('movies_df.joblib')
    similarity = joblib.load('similarity_bollywood.joblib')

    def recommend(movie):
        movie = movie.lower()
        try:
            movie_index = df[df['Movie_Name'] == movie].index[0]
            distances = similarity[movie_index]
            movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:7]

            recommended_movies = []
            recommended_posters = []
            for i in movie_list:
                title = df.iloc[i[0]].Movie_Name.title()
                recommended_movies.append(title)
                movie_id = get_movie_id(title)
                time.sleep(0.3)  # Rate limiting
                if movie_id:
                    recommended_posters.append(fetch_poster(movie_id))
                else:
                    recommended_posters.append("https://via.placeholder.com/300x450?text=No+Image")
            return recommended_movies, recommended_posters
        except IndexError:
            st.warning(f"Movie '{movie.title()}' not found in the Bollywood dataset.")
            return [], []

    selected_movie = st.selectbox("Select a Bollywood movie:", [''] + list(df['Movie_Name'].str.title().values))

    if selected_movie:
        if st.button("Get Recommendations"):
            recommended_movies, recommended_posters = recommend(selected_movie.lower())
            if recommended_movies:
                st.subheader("You might also like:")
                cols = st.columns(3)
                for i in range(len(recommended_movies)):
                    with cols[i % 3]:
                        st.image(recommended_posters[i], use_container_width=True)
                        st.caption(recommended_movies[i])
            st.markdown("---")

    col_back = st.columns([1, 2, 1])
    with col_back[1]:
        if st.button("🔙 Back to Genres"):
            st.session_state.page = 'home'
            st.rerun()

# 🎬 Hollywood Page
def hollywood_page():
    st.title("🎬 Hollywood Movie Recommender")
    st.markdown("*Explore recommendations from the world of Hollywood!*")
    st.markdown("---")

    new_df = joblib.load('new_df.joblib')
    h_similarity = joblib.load('similarity_hollywood.joblib')

    def recommend(movie):
        movie = movie.lower().strip()
        df = new_df.reset_index(drop=True)
        matches = df[df['title'].str.lower().str.strip() == movie]
        if matches.empty:
            st.warning(f"Movie '{movie.title()}' not found in the Hollywood dataset.")
            return [], []

        movie_index = matches.index[0]
        distances = h_similarity[movie_index]
        movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:7]

        recommended_movies = []
        recommended_posters = []
        for i in movie_list:
            title = df.iloc[i[0]]['title'].title()
            movie_id = df.iloc[i[0]].movie_id
            time.sleep(0.3)  # Rate limiting
            recommended_movies.append(title)
            recommended_posters.append(fetch_poster(movie_id))
        return recommended_movies, recommended_posters

    selected_movie = st.selectbox("Select a Hollywood movie:", [''] + list(new_df['title'].str.title().values))

    if selected_movie:
        if st.button("Get Recommendations"):
            recommended_movies, recommended_posters = recommend(selected_movie.lower())
            if recommended_movies:
                st.subheader("You might also enjoy:")
                cols = st.columns(3)
                for i in range(len(recommended_movies)):
                    with cols[i % 3]:
                        st.image(recommended_posters[i], use_container_width=True)
                        st.caption(recommended_movies[i])
            st.markdown("---")

    col_back_h = st.columns([1, 2, 1])
    with col_back_h[1]:
        if st.button("🔙 Back to Genres"):
            st.session_state.page = 'home'
            st.rerun()

# 🚦 Routing
if st.session_state.page == 'home':
    home()
elif st.session_state.page == 'bollywood':
    bollywood_page()
elif st.session_state.page == 'hollywood':
    hollywood_page()