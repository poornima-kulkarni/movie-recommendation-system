import streamlit as st
import joblib
import requests

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=55fe9c3ae3ab375e35137377c11e42de&language=en-US"
    response = requests.get(url)
    data = response.json()

    if 'poster_path' in data and data['poster_path']:
        return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
    else:
        return "https://via.placeholder.com/500x750?text=No+Image"


# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'home'


# Home page
def home():
    st.title("🎬 Movie Recommender")
    st.write("Welcome! Please choose a category below.")

    st.markdown("---")  # divider line

    #st.markdown("<br><br><br>", unsafe_allow_html=True)  # spacing

    # Buttons 
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Bollywood"):
                st.session_state.page = 'bollywood'
                st.rerun()
        with col_btn2:
            if st.button("Hollywood"):
                st.session_state.page = 'hollywood'
                st.rerun()
    

# Bollywood page
def bollywood_page():
    st.title("🎥 Bollywood Movie Recommender")

    # Load data
    df = joblib.load('movies_df.joblib')
    similarity = joblib.load('similarity_matrix.joblib')

    def get_movie_id(movie_name):
            url = "https://api.themoviedb.org/3/search/movie"
            params = {
                "api_key": "55fe9c3ae3ab375e35137377c11e42de",
                "query": movie_name
            }
            response = requests.get(url, params=params)
            data = response.json()
            if data["results"]:
                return data["results"][0]["id"]
            return None

    # Recommend function for bollywood
    def recommend(movie):
        movie = movie.lower()
        movie_index = df[df['Movie_Name'] == movie].index[0]
        distances = similarity[movie_index]
        movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        
        recommended_movies = []
        recommended_posters = []
        for i in movie_list:
            title = df.iloc[i[0]].Movie_Name.title()
            recommended_movies.append(df.iloc[i[0]].Movie_Name.title())
            movie_id = get_movie_id(title)
            if movie_id:
                recommended_posters.append(fetch_poster(movie_id))
            else:
                recommended_posters.append("https://via.placeholder.com/500x750?text=No+Image")
        return recommended_movies, recommended_posters
        

    selected_movie = st.selectbox("Select a movie:", df['Movie_Name'].str.title().values)

    # Center the Recommend and Go Back buttons
    # Center the Recommend button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        recommend_clicked = st.button("Recommend")

    if recommend_clicked:
        recommended_movies, recommended_posters = recommend(selected_movie)
        
        st.subheader("Recommended Movies:")

        # Display recommended movies in 3 columns, full width outside button columns
        poster_cols = st.columns(3)
        for i in range(len(recommended_movies)):
            with poster_cols[i % 3]:
                st.image(recommended_posters[i], width=500, use_container_width=True)
                st.write(recommended_movies[i])

    st.markdown("<br>", unsafe_allow_html=True)

    # Center the Go Back button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔙 Go Back"):
            st.session_state.page = 'home'
            st.rerun()

# Placeholder for Hollywood
def hollywood_page():
    st.title("🎬 Hollywood Movie Recommender")

    new_df = joblib.load('new_df.joblib')
    h_similarity = joblib.load('new_similarity.joblib')

    # recommend function for hollywood
    def recommend(movie):
        movie = movie.lower().strip()
        
        # Work with a reset index version of new_df
        df = new_df.reset_index(drop=True)

        matches = df[df['title'].str.lower().str.strip() == movie]

        if matches.empty:
            st.warning(f"Movie '{movie}' not found in dataset.")
            return []

        # Now, this index is safe to use with similarity matrix
        movie_index = matches.index[0]

        distances = h_similarity[movie_index]
        movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:7]

        recommended_movies = []
        recommended_movies_posters = []

        for i in movie_list:
            recommended_movies.append(df.iloc[i[0]]['title'].title())
            movie_id = df.iloc[i[0]].movie_id
            recommended_movies_posters.append(fetch_poster(movie_id))

        return recommended_movies, recommended_movies_posters


    selected_movie = st.selectbox("Select a movie:", new_df['title'].str.title().values)

   # Center the Recommend button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        recommend_clicked = st.button("Recommend")

    if recommend_clicked:
        recommended_movies, recommended_posters = recommend(selected_movie)
        
        st.subheader("Recommended Movies:")

        # Display recommended movies in 3 columns, full width outside button columns
        poster_cols = st.columns(3)
        for i in range(len(recommended_movies)):
            with poster_cols[i % 3]:
                st.image(recommended_posters[i], width=500, use_container_width=True)
                st.write(recommended_movies[i])

    st.markdown("<br>", unsafe_allow_html=True)

    # Center the Go Back button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔙 Go Back"):
            st.session_state.page = 'home'
            st.rerun()

# Routing
if st.session_state.page == 'home':
    home()
elif st.session_state.page == 'bollywood':
    bollywood_page()
elif st.session_state.page == 'hollywood':
    hollywood_page()
