import streamlit as st
import requests
import time

st.set_page_config(page_title="Your Personalized Movie Recommendations")
st.write("Instructions: Select your top 5 favorite and top 5 least liked movies, and click 'Get Recommendations' to view movie recommendations and top genres.")

st.title("Get Your AI-Powered Movie Recommendations 🎬🤖🍿", anchor="center")

# API endpoint 
recommendations_endpoint = "https://filmaholic-api-cogu3u3naq-uc.a.run.app/predict"

# reads list of movies saved in this text file, needs to be updated once new movies added; note: ASIN formatting
with open("filmaholic/interface/movies2.txt", "r", encoding="cp1252") as file:
    movies_list = [line.strip() for line in file]

st.subheader("Select Your Favorite Movies:")
selected_movies_best = [st.selectbox(f"Select Favorite Movie {i+1}", movies_list, key=f"best_movie_{i}") for i in range(5)]

st.subheader("Select Your Least Favorite Movies:")
selected_movies_least_liked = [st.selectbox(f"Select Least Favorite Movie {i+1}", movies_list, key=f"least_liked_movie_{i}") for i in range(5)]

# combining most liked and disliked into single list for API
selected_movies = selected_movies_best + selected_movies_least_liked

# function to receive movie recommendations and top genres from API
def get_recommendations_and_genres(selected_movies_fav, selected_movies_dislike):
    try:
        # JSON payload with selected movies
        
        }
        params = {
        'liked_movies': selected_movies_fav,  
        'disliked_movies': selected_movies_dislike
        }

        # Make a POST request to the recommendations endpoint
        response = requests.post(url, json=params)

        # checks if the request was successful; add genre to return term if we want to include
        if response.status_code == 200:
            data = response.json()
            recommendations = data.get("Suggested Movies", [])
            # top_genres = data.get("Top Genres", [])
            return recommendations
        else:
            st.error(f"Error fetching recommendations: {response.status_code}")
            return []

    except requests.exceptions.RequestException as e:
        st.error(f"API request error: {e}")
        return []

# Function to mimic a 30-second loading process
def simulate_loading():
    st.write("Calculating your results...")
    progress_bar = st.progress(0)

    num_steps = 100
    step_interval = 30 / num_steps

    for i in range(num_steps + 1):
        progress_bar.progress(i)
        time.sleep(step_interval)

    st.success("Calculation Completed!")

# button on UI to get recommendations
# need to add genres to st.button once we can load them
if st.button("Get My Movie Recommendations!"):
    simulate_loading()
    recommendations = get_recommendations_and_genres(selected_movies_best, selected_movies_least_liked)

    if recommendations:
        st.subheader("Your Top 10 Recommended Movies:")
        for i, movie in enumerate(recommendations):
            st.write(f"{i+1}. {movie}")
    else:
        st.info("No recommendations available based on your selections.")

    # Display top genres
    # st.subheader("Top Genres Based on Your Selections:")
    # for i, genre in enumerate(top_genres):
    #    st.write(f"{i+1}. {genre}")
