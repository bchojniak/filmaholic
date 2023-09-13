import re, os, math, datetime, pickle

import pandas as pd
import numpy as np

from pathlib import Path
from google.cloud import bigquery

from filmaholic.ml_logic.data import upload_to_bigquery, upload_to_cloud_platform, get_data_bigquery, get_data_cloud_platform
from filmaholic.params import *

def title_to_id(liked_movies: list, disliked_movies: list):

    movies_mod = get_data_bigquery(GCP_PROJECT, BQ_DATASET, 'movies-mod')

    liked_movies_df = pd.DataFrame({'title': liked_movies})
    disliked_movies_df = pd.DataFrame({'title': disliked_movies})

    liked_movies_df = liked_movies_df.merge(movies_mod, on='title', how='left')
    disliked_movies_df = disliked_movies_df.merge(movies_mod, on='title', how='left')

    return liked_movies_df, disliked_movies_df

def preprocess_genres(liked_movies: list, disliked_movies: list):

    liked_movies_df, disliked_movies_df = title_to_id(liked_movies, disliked_movies)

    total_user_like = pd.DataFrame()
    total_user_dislike = pd.DataFrame()

    liked_movies_df = liked_movies_df.iloc[:, 4:]
    disliked_movies_df = disliked_movies_df.iloc[:, 4:]

    liked_total_counts = 0
    liked_dict = {'War': 0, 'Animation': 0, 'Horror': 0, 'Sci-Fi': 0, 'Fantasy': 0, 'Thriller': 0, 'Crime': 0, 'Mystery': 0,
                    'Documentary': 0, 'Children': 0, 'Action': 0, 'Adventure': 0, 'Musical': 0,'Film-Noir': 0, 'Drama': 0,
                    'Romance': 0, 'Comedy': 0, 'Western': 0, 'None': 0}

    disliked_total_counts = 0
    disliked_dict = {'War': 0, 'Animation': 0, 'Horror': 0, 'Sci-Fi': 0, 'Fantasy': 0, 'Thriller': 0, 'Crime': 0, 'Mystery': 0,
                    'Documentary': 0, 'Children': 0, 'Action': 0, 'Adventure': 0, 'Musical': 0,'Film-Noir': 0, 'Drama': 0,
                    'Romance': 0, 'Comedy': 0, 'Western': 0, 'None': 0}

    for genre in list(liked_movies_df.columns):
        if len(liked_movies_df) == 0:
            pass
        else:
            liked_total_counts += sum(liked_movies_df[genre])

        if len(disliked_movies_df) == 0:
            pass
        else:
            disliked_total_counts += sum(disliked_movies_df[genre])

    for genre in list(liked_movies_df.columns):
        if liked_total_counts == 0:
            pass
        else:
            liked_genre_total_counts = sum(liked_movies_df[genre])
            liked_dict[genre] = liked_genre_total_counts/liked_total_counts

        if disliked_total_counts == 0:
            pass
        else:
            disliked_genre_total_counts = sum(disliked_movies_df[genre])
            disliked_dict[genre] = disliked_genre_total_counts/disliked_total_counts

    user_like_df = pd.DataFrame(liked_dict, index=[0])
    user_dislike_df = pd.DataFrame(disliked_dict, index=[0])

    if len(total_user_like) == 0:
        total_user_like = user_like_df
    else:
        total_user_like = pd.concat([total_user_like, user_like_df], ignore_index= True)

    if len(total_user_dislike) == 0:
        total_user_dislike = user_dislike_df
    else:
        total_user_dislike = pd.concat([total_user_dislike, user_dislike_df], ignore_index= True)

    return total_user_like, total_user_dislike

def preprocess_tags(liked_movies: list, disliked_movies: list):

    liked_movies_df, disliked_movies_df = title_to_id(liked_movies, disliked_movies)

    like_dislike_tags = pd.DataFrame()

    like_tags_df = pd.DataFrame()
    dislike_tags_df = pd.DataFrame()

    vectorized_dict = get_data_cloud_platform(GCP_PROJECT, BUCKET_NAME, 'vectorized_dict', 'vectorized_dict', '.pkl')

    # with open('data/vectorized_dict.pkl', 'rb') as reader:
    #   vectorized_dict = pickle.load(reader)

    for index, row in liked_movies_df.iterrows():

        temp_movie_df = get_data_bigquery(GCP_PROJECT, BQ_DATASET_MOVIES_TAGS, f'{str(int(row.movieId))}')

        if len(like_tags_df) == 0:
            like_tags_df = temp_movie_df
        else:
            like_tags_df = pd.concat([like_tags_df, temp_movie_df], ignore_index= True)

    for index, row in disliked_movies_df.iterrows():

        temp_movie_df = get_data_bigquery(GCP_PROJECT, BQ_DATASET_MOVIES_TAGS, f'{str(int(row.movieId))}')

        if len(dislike_tags_df) == 0:
            dislike_tags_df = temp_movie_df
        else:
            dislike_tags_df = pd.concat([dislike_tags_df, temp_movie_df], ignore_index= True)

    try:
        like_tags_list = list(like_tags_df.tag)
        dislike_tags_list = list(dislike_tags_df.tag)
    except Exception:
        print('exception')

    like_dict = {}
    dislike_dict = {}

    for tag in like_tags_list:
        like_dict[tag] = like_tags_list.count(tag) * -1

    for tag in dislike_tags_list:
        dislike_dict[tag] = dislike_tags_list.count(tag) * -1

    like_tags_counted = sorted(like_dict, key= lambda tag: like_dict[tag])
    dislike_tags_counted = sorted(dislike_dict, key= lambda tag: dislike_dict[tag])

    like_tags_vectorized = []
    dislike_tags_vectorized = []

    if len(like_tags_counted) < 50:
        num_like_tags = len(like_tags_counted)
    else:
        num_like_tags = 50

    if len(dislike_tags_counted) < 50:
        num_dislike_tags = len(like_tags_counted)
    else:
        num_dislike_tags = 50

    for tag in like_tags_counted[:num_like_tags]:
        try:
            tag_vector = vectorized_dict[tag]
            like_tags_vectorized.append(tag_vector)
        except Exception:
            pass

    for tag in dislike_tags_counted[:num_dislike_tags]:
        try:
            tag_vector = vectorized_dict[tag]
            dislike_tags_vectorized.append(tag_vector)
        except Exception:
            pass

    if len(like_tags_vectorized) > 20 or len(dislike_tags_vectorized) > 20:
      like_dislike_dict = {}

      for x in range(20):
          like_dislike_dict['LIKE_' + str(x)] = like_tags_vectorized[x]
          like_dislike_dict['DISLIKE_' + str(x)] = dislike_tags_vectorized[x]

      like_dislike_tags = pd.DataFrame(like_dislike_dict, index=[0])

      like_dislike_tags_int = like_dislike_tags.astype('int64')

      return like_dislike_tags_int
    else:
      return 'Vector not long enough'
