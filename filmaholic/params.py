import os
import numpy as np

################## VARIABLES
GCP_PROJECT = os.environ.get("GCP_PROJECT")
# GCP_REGION = os.environ.get("GCP_REGION")
BQ_DATASET = os.environ.get("BQ_DATASET")
# BQ_REGION = os.environ.get("BQ_REGION")
BUCKET_NAME = os.environ.get("BUCKET_NAME")
# INSTANCE = os.environ.get("INSTANCE")

# GCR_IMAGE = os.environ.get("GCR_IMAGE")
# GCR_REGION = os.environ.get("GCR_REGION")
# GCR_MEMORY = os.environ.get("GCR_MEMORY")

################## CONSTANTS
LOCAL_DATA_PATH = os.path.join(os.path.expanduser('~'), "code", "bchojniak", "filmaholic", "data")
LOCAL_DATA_PATH_FINAL =  os.path.join(os.path.expanduser('~'), "code", "bchojniak", "filmaholic", "data", "final")
LOCAL_DATA_PATH_MOVIE_TAGS =  os.path.join(os.path.expanduser('~'), "code", "bchojniak", "filmaholic", "data", "movie_tags")

# COLUMN_NAMES_RAW = ['fare_amount','pickup_datetime', 'pickup_longitude', 'pickup_latitude', 'dropoff_longitude', 'dropoff_latitude', 'passenger_count']

# DTYPES_RAW = {
#     "fare_amount": "float32",
#     "pickup_datetime": "datetime64[ns, UTC]",
#     "pickup_longitude": "float32",
#     "pickup_latitude": "float32",
#     "dropoff_longitude": "float32",
#     "dropoff_latitude": "float32",
#     "passenger_count": "int16"
# }
