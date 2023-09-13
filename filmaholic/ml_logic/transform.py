import pandas as pd

def create_like_dislike_tags():

    # import tags_subset.csv
    # import ratings_subset.csv

    tags_unique_users = list(tags.drop_duplicates('userId').userId)

    like_dislike_tags = pd.DataFrame()

    progress_counter = 0

    with open('data/final/vectorized_dict.pkl', 'rb') as reader:
        vectorized_dict = pickle.load(reader)

    for user in tags_unique_users:
        progress_counter += 1
        print(progress_counter)

        temp_ratings_df = ratings[ratings.userId == user]
        like_tags_df = pd.DataFrame()
        dislike_tags_df = pd.DataFrame()

        for index, row in temp_ratings_df.iterrows():
            try:
                if row.rating >= 4:
                    # temp_movie_df = pd.read_csv('data/movies_tags/{}.csv'.format(str(int(row.movieId))))

                    if len(like_tags_df) == 0:
                        like_tags_df = temp_movie_df

                    else:
                        like_tags_df = pd.concat([like_tags_df, temp_movie_df], ignore_index= True)

                else:
                    # temp_movie_df = pd.read_csv('data/movies_tags/{}.csv'.format(str(int(row.movieId))))

                    if len(dislike_tags_df) == 0:
                        dislike_tags_df = temp_movie_df

                    else:
                        dislike_tags_df = pd.concat([dislike_tags_df, temp_movie_df], ignore_index= True)
            except Exception:
                print('exception 1')
                pass

        try:
            like_tags_list = list(like_tags_df.tag)
            dislike_tags_list = list(dislike_tags_df.tag)
        except Exception:
            print('exception 2')
            continue

        like_dict = {}
        dislike_dict = {}

        for tag in like_tags_list:
            like_dict[tag] = like_tags_list.count(tag) * -1

        for tag in dislike_tags_list:
            dislike_dict[tag] = dislike_tags_list.count(tag) * -1

        like_tags_counted = sorted(like_dict, key=lambda tag: like_dict[tag])
        dislike_tags_counted = sorted(dislike_dict, key=lambda tag: dislike_dict[tag])

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

        if len(like_tags_vectorized) < 20 or len(dislike_tags_vectorized) < 20:
            continue

        like_dislike_dict = {}

        like_dislike_dict['userId'] = user

        for x in range(20):
            like_dislike_dict['LIKE_' + str(x)] = like_tags_vectorized[x]
            like_dislike_dict['DISLIKE_' + str(x)] = dislike_tags_vectorized[x]

        concat_df = pd.DataFrame(like_dislike_dict, index=[0])

        if len(like_dislike_tags) == 0:
            like_dislike_tags = concat_df

        else:
            like_dislike_tags = pd.concat([like_dislike_tags, concat_df], ignore_index= True)

    # like_dislike_tags_int = like_dislike_tags.astype('int64')
    # like_dislike_tags_int.to_csv('data/final/like_dislike_tags.csv', index = False)

def create_movie_tags_csvs():

    # import tags_subset.csv

    # import movies_mod.csv and create movies_list

    for i, movieId in enumerate(movies_list):
        tags.movieId = tags.movieId.astype('string')
        tags_movie = tags[tags.movieId == movieId].copy().drop('movieId', axis=1)
        tags_movie['COUNT'] = 1
        tags_movies_counts = tags_movie.groupby(['tag']).count()
        tags_movies_counts = tags_movies_counts.sort_values(by=['COUNT'], ascending= False).reset_index()

        # tags_movies_counts.to_csv('data/movies_tags/' + str(movieId) + '.csv', index = False)

        print(f'csv {i} created')
