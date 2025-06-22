import streamlit as st
import pandas as pd
import time
from datetime import datetime

st.set_page_config(page_title="🎥 Real-Time Movie Ratings", layout="wide")
st.title("🎬 Real-Time Movie Recommendation Dashboard")

MOVIES_FILE = "moviesrealtimedata.csv"
RATINGS_FILE = "ratings.csv"

movies_df = pd.read_csv(MOVIES_FILE)
movies_df["title"] = movies_df["title"].str.strip()

# -------------------------------
# 📤 Sidebar: User Rating Input
# -------------------------------
# Sidebar: New Movie Rating Input by Genre
st.sidebar.header("🎥 Submit a New Movie Rating by Genre")
with st.sidebar.form("genre_rating_form"):
    new_movie_title = st.text_input("Enter Movie Title")
    romance = st.slider("Romance", 1.0, 10.0, 1.0)
    comedy = st.slider("Comedy", 1.0, 10.0, 1.0)
    drama = st.slider("Drama", 1.0, 10.0, 1.0)
    horror = st.slider("Horror", 1.0, 10.0, 1.0)
    thriller = st.slider("Thriller", 1.0, 10.0, 1.0)
    mystery = st.slider("Mystery", 1.0, 10.0, 1.0)
    submitted_genre = st.form_submit_button("Submit Movie")

if submitted_genre and new_movie_title:
    genre_ratings = {
        "Romance": romance,
        "Comedy": comedy,
        "Drama": drama,
        "Horror": horror,
        "Thriller": thriller,
        "Mystery": mystery
    }

    # Filter out genres with default rating (1.0)
    rated_genres = {genre: rating for genre, rating in genre_ratings.items() if rating > 1.0}

    if not rated_genres:
        st.sidebar.warning("Please rate at least one genre (rating > 1.0) to add the movie.")
    else:
        # Get genres to append
        genre_string = "|".join(rated_genres.keys())

        # Get the genre with the highest rating
        top_genre = max(rated_genres, key=rated_genres.get)
        top_rating = rated_genres[top_genre]

        # Generate new movie_id
        if movies_df.empty:
            new_movie_id = 1
        else:
            new_movie_id = movies_df["movie_id"].max() + 1

        # Append to movies CSV
        new_movie_row = pd.DataFrame([[new_movie_id, new_movie_title.strip(), genre_string]],
                                     columns=["movie_id", "title", "genre"])
        new_movie_row.to_csv(MOVIES_FILE, mode='a', header=False, index=False)

        # Append ratings for each genre with rating > 1.0
        timestamp = int(datetime.utcnow().timestamp())
        with open(RATINGS_FILE, "a") as f:
            for genre, rating_value in rated_genres.items():
                f.write(f"{new_movie_id},{rating_value},{timestamp}\n")

        # Show only top genre to user
        st.sidebar.success(f"'{new_movie_title}' added as a **{top_genre}** movie with rating **{top_rating}** ⭐")




# -------------------------------
# 📊 Main Analytics Dashboard
# -------------------------------
selected_genre = st.selectbox("🎭 Choose a Genre", movies_df["genre"].unique())
placeholder = st.empty()

def get_live_ratings():
    try:
        ratings = pd.read_csv(RATINGS_FILE, names=["movie_id", "rating", "timestamp"])
        ratings["timestamp"] = pd.to_datetime(ratings["timestamp"], unit="s")
        return ratings
    except FileNotFoundError:
        return pd.DataFrame(columns=["movie_id", "rating", "timestamp"])

while True:
    ratings_df = get_live_ratings()

    if not ratings_df.empty:
        merged = ratings_df.merge(movies_df, on="movie_id")

        # Overall top movies
        overall_avg = merged.groupby("title")["rating"].mean().sort_values(ascending=False).head(5)
        top_overall_movie = overall_avg.idxmax()
        top_overall_rating = overall_avg.max()

        # Genre-based top movies
        genre_filtered = merged[merged["genre"].str.contains(selected_genre, case=False, na=False)]
        top_genre_avg = genre_filtered.groupby("title")["rating"].mean().sort_values(ascending=False).head(5)
        top_genre_movie = top_genre_avg.idxmax() if not top_genre_avg.empty else "N/A"
        top_genre_rating = top_genre_avg.max() if not top_genre_avg.empty else 0

        # Pie Chart Data: Genre rating count
        genre_counts = merged["genre"].value_counts()

        with placeholder.container():
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📈 Top 5 Rated Movies (Overall)")
                st.bar_chart(overall_avg)

            with col2:
                st.subheader(f"🎭 Top 5 in '{selected_genre}' Genre")
                st.bar_chart(top_genre_avg)

            st.markdown("---")
            st.subheader("🥧 Genre Popularity Based on Ratings")
            st.plotly_chart({
                "data": [{
                    "values": genre_counts.values,
                    "labels": genre_counts.index,
                    "type": "pie",
                    "hole": 0.3
                }],
                "layout": {"title": "Most Rated Genres"}
            })

            st.markdown("### 🏆 Movie Highlights")
            st.success(f"Top Rated Movie Overall: **{top_overall_movie}** with average rating **{top_overall_rating:.2f}** ⭐")
            if top_genre_movie != "N/A":
                st.info(f"Top Rated in '{selected_genre}': **{top_genre_movie}** with rating **{top_genre_rating:.2f}**")
            else:
                st.warning("Not enough ratings in this genre yet.")
    else:
        with placeholder.container():
            st.info("Waiting for ratings... Add some using the sidebar.")

    time.sleep(5)