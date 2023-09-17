import re, os, math, datetime, pickle, joblib

import pandas as pd
import numpy as np

from pathlib import Path
from google.cloud import bigquery
from google.cloud import storage

from tensorflow import keras

def upload_to_bigquery(
    project:str,
    dataset:str,
    table:str,
    df,
    dtype=None
    ):

    t = f"{project}.{dataset}.{table}"
#    df = pd.read_csv(local_path + f"/{table}.csv", dtype=dtype)

    client = bigquery.Client()

    write_mode = "WRITE_TRUNCATE"
    job_config = bigquery.LoadJobConfig(write_disposition=write_mode)

    job = client.load_table_from_dataframe(df, t, job_config=job_config)
    result = job.result()

def upload_to_cloud_platform(
    bucket:str,
    content,
    file_name_cloud:str,
    dtype=None
    ):

    client = storage.Client()
    bucket = client.bucket(bucket)
    blob = bucket.blob(file_name_cloud)
    blob.upload_from_string(content)

def get_data_bigquery(
        project:str,
        dataset:str,
        table_name:str
    ) -> pd.DataFrame:

#    if cache_path.is_file():
#        df = pd.read_csv(cache_path, header='infer' if data_has_header else None)

#    else:

    query = f'SELECT * FROM `{project}.{dataset}.{table_name}`'

    client = bigquery.Client()
    query_job = client.query(query)
    result = query_job.result()
    df = result.to_dataframe()

#        if df.shape[0] > 1:
#            df.to_csv(cache_path, header=data_has_header, index=False)

    return df

def get_data_cloud_platform(
    project:str,
    bucket:str,
    file_name_cloud:str,
    file_name_local:str,
    format:str
    ):

    client = storage.Client(project=project)
    bucket = client.bucket(bucket)
    blob = bucket.blob(file_name_cloud + format)
    blob.download_to_filename(file_name_local + format)

    if format == '.h5':
        file = keras.models.load_model(f'{file_name_local}.h5', compile=True)

    if format == '.sav':
        file = joblib.load(open(f'{file_name_local}.sav', 'rb'))

    if format == '.pkl':
        with open(f'{file_name_local}.pkl', 'rb') as reader:
            file = joblib.load(reader)

    return file
