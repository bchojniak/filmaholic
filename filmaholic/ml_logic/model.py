import re, os, math, datetime, pickle

import pandas as pd
import numpy as np

from pathlib import Path
from google.cloud import bigquery

from tensorflow import keras
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import classification_report
from sklearn.utils import shuffle
from sklearn.linear_model import LinearRegression

from filmaholic.ml_logic.data import upload_to_bigquery, upload_to_cloud_platform, get_data_bigquery, get_data_cloud_platform
from filmaholic.params import *


def top_10_recommendations(liked_movies: list, disliked_movies: list, like_genres, dislike_genres, like_dislike_tags):

    movies_mod = get_data_bigquery(GCP_PROJECT, BQ_DATASET, 'movies-mod')

    watched = liked_movies + disliked_movies

    # identifying not watched movies
    not_watched = list(movies_mod.movieId)

    for movie in watched:
        if movie in not_watched:
            not_watched.remove(movie)

    # genres

    # changing column names to differenciate liked genres and disliked genres, and movie genres
    like_columns = list(like_genres.columns)
    like_columns_modified = []
    for column in like_columns:
        modify_column = 'user_like_' + column
        like_columns_modified.append(modify_column)
    like_genres.columns = like_columns_modified

    dislike_columns = list(dislike_genres.columns)
    dislike_columns_modified = []
    for column in dislike_columns:
        modify_column = 'user_dislike_' + column
        dislike_columns_modified.append(modify_column)
    dislike_genres.columns = dislike_columns_modified

    # adding 'fake' movieId of -1 to the 3 dfs

    like_genres['userId'] = -999
    dislike_genres['userId'] = -999
    like_dislike_tags['userId'] = -999

    # tags

    movie_tags_df = get_data_bigquery(GCP_PROJECT, BQ_DATASET, 'movie-tags-df')

    # adding a column with all not watched movies, then merging movie information (genres and tags profiles of movies)
    template_df = pd.DataFrame({'movieId': not_watched}, index= list(range(len(not_watched))))
    template_df = template_df.merge(movies_mod, how= 'left', on= 'movieId').dropna()
    template_df = template_df.merge(movie_tags_df, how= 'left', on= 'movieId').dropna()
    del movie_tags_df

    # adding a column with the userId on all rows, then merging user information (genres and tags profiles of users)
    template_df['userId'] = -999
    template_df = template_df.merge(like_genres, how= 'left', on= 'userId').dropna()
    del like_genres
    template_df = template_df.merge(dislike_genres, how= 'left', on= 'userId').dropna()
    del dislike_genres
    template_df = template_df.merge(like_dislike_tags, how= 'left', on= 'userId').dropna()
    del like_dislike_tags

    # generating the columns for the random forest input
    rf_columns = []
    for x in range(20):
        rf_columns.append('LIKE_' + str(x))
        rf_columns.append('DISLIKE_' + str(x))
    for x in range(5):
        rf_columns.append('TAG_' + str(x))

    # separating the 3 inputs for the neural network
    genres_like_input = template_df.loc[:, like_columns_modified]
    genres_dislike_input = template_df.loc[:, dislike_columns_modified]
    genres_movie_input = template_df.loc[:, like_columns]

    # separating the input for the random forest
    tags_input = template_df.loc[:, rf_columns]

    # saving a list with the not-watched movieIds
    movieId_list = list(template_df.movieId)

    del template_df

    # loading models
    genres_model = get_data_cloud_platform(GCP_PROJECT, BUCKET_NAME, 'genres_model', 'genres_model', '.h5')
    # genres_model = keras.models.load_model('models/genres_model.h5', compile=True)
    tags_model = get_data_cloud_platform(GCP_PROJECT, BUCKET_NAME, 'tags_model', 'tags_model', '.sav')
    # tags_model = pickle.load(open('models/tags_model.sav', 'rb'))
    combine_model = get_data_cloud_platform(GCP_PROJECT, BUCKET_NAME, 'combine_model', 'combine_model', '.sav')
    # combine_model = pickle.load(open('models/combine_model.sav', 'rb'))

    # predicting with the genres and tags models
    genres_model_predictions = (genres_model.predict(x= [genres_like_input, genres_dislike_input, genres_movie_input])) * 5
    tags_model_predictions = tags_model.predict(tags_input)

    # transforming the neural network prediction into a list
    genres_model_predictions_list = []
    for prediction in genres_model_predictions:
        genres_model_predictions_list.append(prediction[0])

    # using both predictions to predict with the combined model
    combine_input = pd.DataFrame({'genres_model': genres_model_predictions_list,
                                  'tag_model': tags_model_predictions},
                                 index= list(range(len(genres_model_predictions))))
    combine_model_predictions = combine_model.predict(combine_input)

    # rounding predictions that end up out of bounds
    combine_model_predictions_rounded = []
    for prediction in combine_model_predictions:
        rounded = prediction
        if rounded > 5:
            rounded = 5
        elif rounded < 0.5:
            rounded = 0.5
        combine_model_predictions_rounded.append(rounded)

    # creating dataframe with predictions
    # predictions_df = pd.DataFrame({'movieId': movieId_list,
    #                                'genres_predictions': genres_model_predictions_list,
    #                               'tags_predictions': tags_model_predictions,
    #                               'combine_predictions': combine_model_predictions_rounded},
    #                              index= list(range(len(movieId_list))))

    predictions_df = pd.DataFrame({'movieId': movieId_list,
                              'prediction': combine_model_predictions_rounded},
                              index= list(range(len(movieId_list))))

    # getting top and bottom predictions
    best_movies_df = predictions_df.sort_values(by=['prediction'], ascending=False).iloc[:20, :]
    worst_movies_df = predictions_df.sort_values(by=['prediction'], ascending=True).iloc[:20, :]

    # adding rest of information about the movie
    best_movies_df = best_movies_df.merge(movies_mod, how= 'left', on= 'movieId').dropna()
    worst_movies_df = worst_movies_df.merge(movies_mod, how= 'left', on= 'movieId').dropna()
    del movies_mod

    return predictions_df, best_movies_df, worst_movies_df
