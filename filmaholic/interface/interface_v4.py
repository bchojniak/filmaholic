import streamlit as st
import requests

# API endpoint (update this with your FastAPI server URL)
recommendations_endpoint = "http://localhost:8000/predict"

# Read the list of movies from the text file
with open("movies2.txt", "r", encoding="cp1252") as file:
    movies_list = [line.strip() for line in file]

# Add subheaders to indicate the purpose of the select boxes
st.subheader("Select Your Top 5 Best Movies:")

selected_movies_best = [st.selectbox(f"Select Movie (Best) {i+1}", movies_list, key=f"best_movie_{i}") for i in range(5)]
st.subheader("Select Your Top 5 Least Liked Movies:")

selected_movies_least_liked = [st.selectbox(f"Select Movie (Least Liked) {i+1}", movies_list, key=f"least_liked_movie_{i}") for i in range(5)]

# Combine the selected movies into a single list
selected_movies = selected_movies_best + selected_movies_least_liked

# Function to get movie recommendations and top genres from the API
def get_recommendations_and_genres(selected_movies_fav, selected_movies_dislike):
    try:
        # Create a JSON payload with selected movies
        payload = {
            "liked_movies": selected_movies_fav,
            "disliked_movies": selected_movies_dislike
        }

        # Make a POST request to the recommendations endpoint
        response = requests.get(recommendations_endpoint, params=payload)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            recommendations = data.get("Suggested Movies", [])
            top_genres = data.get("Top Genres", [])
            return recommendations, top_genres
        else:
            st.error(f"Error fetching recommendations: {response.status_code}")
            return [], []

    except requests.exceptions.RequestException as e:
        st.error(f"API request error: {e}")
        return [], []

# Create a button to fetch movie recommendations and top genres
if st.button("Get Recommendations"):
    recommendations, top_genres = get_recommendations_and_genres(selected_movies_best, selected_movies_least_liked)

    if recommendations:
        st.subheader("Recommended Movies:")
        for i, movie in enumerate(recommendations):
            st.write(f"{i+1}. {movie}")
    else:
        st.info("No recommendations available based on your selections.")

    # Display top genres
    st.subheader("Top Genres Based on Your Selections:")
    for i, genre in enumerate(top_genres):
        st.write(f"{i+1}. {genre}")

if __name__ == "__main__":
    st.set_page_config(page_title="Your Personalized Movie Recommendations")
    st.write("Instructions: Select your top 5 favorite and top 5 least liked movies, and click 'Get Recommendations' to view movie recommendations and top genres.")
