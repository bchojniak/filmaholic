import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
#from taxifare.ml_logic.preprocessor import preprocess_features    -> do this but for our project (getting from cloud)
#from taxifare.ml_logic.registry import load_model                 -> do this but for our project (getting from cloud)
from data_managing.preprocessor import preprocess_genres, preprocess_tags, title_to_id
from data_managing.model import top_10_recommendations

app = FastAPI()

# Allowing all middleware is optional, but good practice for dev purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.state.model = top_10_recommendations

#no projeto abaixo, usando esses dados, eles fazem um predict do preço da viagem
#no nosso projeto, vamos usar os inputs pra fazer o predict da sugestao de filme?
# inputs is liked movies and 10 dislikes --> from that we can tell the 10 recommendations
# so the inputs will be connected to the model, and prediction will come from that


# http://127.0.0.1:8000/predict?pickup_datetime=2012-10-06 12:10:20&pickup_longitude=40.7614327&pickup_latitude=-73.9798156&dropoff_longitude=40.6513111&dropoff_latitude=-73.8803331&passenger_count=2
@app.get("/predict")
def predict(
    liked_movies: list[str],
    disliked_movies: list[str]
):      # 1
    """
    Make a single course prediction with 10 movies and respective predicted rating
    """

    #X_pred = pd.DataFrame(locals(), index=[0])

    model = app.state.model
    assert model is not None

    liked, disliked = title_to_id(liked_movies: list, disliked_movies: list)
    like_genres, dislike_genres = preprocess_genres(liked_movies: list, disliked_movies: list)
    like_dislike_tags = preprocess_tags(liked_movies: list, disliked_movies: list)

    # liked_processed, disliked_processed = preprocess_features(liked_movies,disliked_movies)

    suggested_movies, best_movies, worst_movies = model.predict(liked, disliked, like_genres, dislike_genres, like_dislike_tags)

    return suggested_movies


@app.get("/")
def root():
    return {'greeting': 'hello'}
