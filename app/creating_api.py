import pandas as pd
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from filmaholic.ml_logic.preprocessor import preprocess_genres, preprocess_tags
from filmaholic.ml_logic.model import top_10_recommendations

app = FastAPI()

# Allowing all middleware is optional, but good practice for dev purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# app.state.model = top_10_recommendations


@app.post("/predict")
async def predict(args:Request):

    args = await args.json()

    # model = app.state.model
    # assert model is not None

    liked_movies = args['liked_movies']
    disliked_movies = args['disliked_movies']

    print(liked_movies)
    print(disliked_movies)

    like_genres, dislike_genres = preprocess_genres(liked_movies, disliked_movies)
    like_dislike_tags = preprocess_tags(liked_movies, disliked_movies)
    predictions, best_movies, worst_movies = top_10_recommendations(liked_movies, disliked_movies, like_genres, dislike_genres, like_dislike_tags)

    return {'Suggested Movies': best_movies.to_dict()}


@app.get("/")
def root():
    return {'greeting': 'hello'}
