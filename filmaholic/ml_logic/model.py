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

from filmaholic.ml_logic.preprocessor import title_to_id


def top_10_recommendations(liked_movies: list, disliked_movies: list, like_genres, dislike_genres, like_dislike_tags):

    liked_movies, disliked_movies = title_to_id(liked_movies, disliked_movies)

    liked_movies = list(liked_movies.movieId)
    disliked_movies = list(disliked_movies.movieId)

    movies_mod = get_data_bigquery(GCP_PROJECT, BQ_DATASET, 'movies_mod')

    watched = liked_movies + disliked_movies

    # identifying not watched movies
    not_watched = [260, 1270, 1196, 1198, 1210, 1240, 1291, 1036, 858, 2716, 1214, 1097, 1136, 541, 1258, 1200, 592, 1197, 2115, 1193, 1206, 924, 2011, 1961, 2918, 1387, 1222, 1221, 919, 1208, 1246, 1968, 2174, 2987, 111, 2797, 1073, 1101, 2000, 1259, 750, 2791, 1080, 1219, 1220, 1307, 912, 1954, 1079, 3527, 2571, 356, 296, 593, 318, 480, 1580, 2762, 1, 2858, 2959, 589, 1265, 3578, 780, 110, 47, 2028, 50, 1682, 608, 1721, 527, 1527, 1704, 32, 2628, 4226, 3793, 377, 364, 1089, 457, 648, 150, 1732, 367, 588, 2997, 3147, 3996, 1923, 380, 293, 4022, 500, 1517, 733, 1617, 2683, 344, 3114, 4027, 2706, 778, 1917, 2329, 1573, 1653, 231, 1584, 1784, 3948, 4011, 595, 2617, 1393, 736, 165, 2, 4993, 4306, 5952, 7153, 6539, 5349, 4963, 5445, 6377, 6874, 4886, 4995, 5418, 5989, 4896, 33794, 7438, 8961, 6365, 7361, 5378, 4973, 4878, 58559, 8636, 5816, 6333, 44191, 32587, 6711, 8360, 8368, 33493, 6934, 79132, 8665, 5218, 59315, 8874, 48516, 8644, 5459, 60069, 49272, 7147, 5502, 6373, 48780, 72998, 4370, 4979, 6502, 6863, 68157, 51662, 45722, 5618, 40815, 4308, 46578, 48394, 55820, 4246, 7143, 68954, 50872, 54286, 4720, 7254, 5679, 5010, 56367, 35836, 6378, 70286, 48774, 5669, 6537, 69122, 56174, 33679, 30793, 4447, 30707, 4816, 4848, 5481, 48385, 5956, 63082, 34048, 5299, 74458, 51255, 4270, 68358, 5995, 4975, 4643, 4776, 91529, 99114, 89745, 109487, 112852, 91500, 134130, 104841, 106782, 122882, 88125, 87232, 96610, 122886, 98809, 109374, 111759, 96079, 86332, 115713, 88129, 85414, 112556, 134853, 116797, 88140, 84152, 106487, 94864, 106920, 102125, 111362, 91542, 97921, 88744, 110102, 106489, 119145, 97304, 102445, 97938, 91658, 122892, 112183, 94959, 112552, 115617, 106696, 91630, 93840, 95510, 115569, 97913, 103249, 115149, 108932, 139385, 122900, 102903, 92259, 89492, 86882, 93510, 95441, 103228, 117529, 116823, 86880, 95167, 148626, 94777, 103253, 106072, 128360, 97752, 87306, 103042, 118696, 101864, 106100, 87869, 84954, 88163, 90405, 107406, 112623, 105844, 106916, 90866, 86911, 111360, 105504, 88810, 104879, 96821, 89864, 102407, 142488, 86833, 139644, 103335, 84944, 103141, 96737, 112175, 103341, 114180, 103772, 111781, 106002, 106918, 117176, 84772, 104374, 135133, 114662, 115210, 98961, 108190, 112138, 136020, 91535, 112290, 97306, 102123, 114935, 143385, 104913, 99112, 87430, 104211, 96588, 87520, 111659, 90746, 95875, 87222, 138036, 97923, 91077, 83613, 140174, 86190, 92420, 110553, 89904, 98154, 89470, 111364, 103688, 122904, 164179, 152081, 166528, 122922, 122920, 122918, 168252, 176371, 168250, 122916, 122912, 143355, 135143, 152077, 179819, 174055, 171763, 158238, 122926, 135536, 122906, 164909, 122924, 177593, 135569, 187593, 166461, 136864, 166635, 157296, 168248, 177765, 166534, 180031, 166643, 159093, 137857, 163645, 161582, 162606, 185029, 175303, 122914, 187541, 182715, 195159, 160438, 165549, 177615, 158966, 168612, 188301, 162578, 160980, 176101, 169984, 192803, 179401, 168366, 187595, 122896, 122890, 135436, 183897, 152970, 160080, 158872, 175569, 143859, 189333, 168254, 162600, 149406, 173145, 183611, 122898, 168326, 194448, 162350, 135567, 169864, 161131, 167746, 173291, 165551, 161634, 159415, 122910, 163134, 166946, 173941, 189713, 178061, 183869, 159858, 176419, 175661, 177763, 158783, 157699, 192389, 162082, 160271, 189203, 180297, 162602, 182823, 192385, 143347, 179817, 168492, 180497, 193944, 187031, 156387, 174909, 160718, 162598, 171011, 201773, 176751, 161922, 152079, 170875, 180045, 158813, 165347, 167370, 189363, 135426, 194951, 135141, 167036, 152017, 184471, 165101, 170827, 177689, 181315, 168344, 180985, 138210, 177651, 160563, 160954, 193065, 196997, 197711, 156609]

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

    movie_tags_df = get_data_bigquery(GCP_PROJECT, BQ_DATASET, 'movie_tags_df')

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
    genres_like_input = np.asarray(genres_like_input).astype(np.float32)
    genres_dislike_input = template_df.loc[:, dislike_columns_modified]
    genres_dislike_input = np.asarray(genres_like_input).astype(np.float32)
    genres_movie_input = template_df.loc[:, like_columns]
    genres_movie_input = np.asarray(genres_like_input).astype(np.float32)


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
    genres_model_predictions = (genres_model.predict(x=[genres_like_input, genres_dislike_input, genres_movie_input])) * 5
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
