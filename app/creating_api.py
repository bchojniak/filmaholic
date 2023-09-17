import pandas as pd
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from filmaholic.ml_logic.preprocessor import preprocess_genres, preprocess_tags
from filmaholic.ml_logic.data import get_data_cloud_platform
from filmaholic.ml_logic.model import top_10_recommendations
from filmaholic.params import *

app = FastAPI()

# Allowing all middleware is optional, but good practice for dev purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.state.genres_model = get_data_cloud_platform(GCP_PROJECT, BUCKET_NAME, 'genres_model', 'genres_model', '.h5')
app.state.tags_model = get_data_cloud_platform(GCP_PROJECT, BUCKET_NAME, 'tags_model', 'tags_model', '.sav')
app.state.combine_model = get_data_cloud_platform(GCP_PROJECT, BUCKET_NAME, 'combine_model', 'combine_model', '.sav')


@app.post("/predict")
async def predict(args:Request):

    args = await args.json()

    genres_model = app.state.genres_model
    tags_model = app.state.tags_model
    combine_model = app.state.combine_model

    assert genres_model is not None
    assert tags_model is not None
    assert combine_model is not None

    liked_movies = args['liked_movies']
    disliked_movies = args['disliked_movies']

    print(liked_movies)
    print(disliked_movies)

    like_genres, dislike_genres = preprocess_genres(liked_movies, disliked_movies)
    like_dislike_tags = preprocess_tags(liked_movies, disliked_movies)
    predictions, best_movies, worst_movies = top_10_recommendations(liked_movies, disliked_movies, like_genres, dislike_genres, like_dislike_tags, genres_model, tags_model, combine_model)

    return {'movies': best_movies.to_dict()}


@app.get("/")
def root():
    return {'greeting': 'hello'}
