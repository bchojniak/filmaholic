import os
import numpy as np

# VARIABLES
GCP_PROJECT = os.environ.get("GCP_PROJECT")
BQ_DATASET = os.environ.get("BQ_DATASET")
BQ_DATASET_MOVIES_TAGS = os.environ.get("BQ_DATASET_MOVIES_TAGS")
BUCKET_NAME = os.environ.get("BUCKET_NAME")

# CONSTANTS
LOCAL_DATA_PATH = os.path.join(os.path.expanduser('~'), "code", "bchojniak", "filmaholic", "data")
LOCAL_DATA_PATH_FINAL =  os.path.join(os.path.expanduser('~'), "code", "bchojniak", "filmaholic", "data", "final")
LOCAL_DATA_PATH_MOVIE_TAGS =  os.path.join(os.path.expanduser('~'), "code", "bchojniak", "filmaholic", "data", "movie_tags")
