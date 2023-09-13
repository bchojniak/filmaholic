import re, os, math, datetime, pickle

import pandas as pd
import numpy as np

from pathlib import Path
from google.cloud import bigquery
from google.cloud import storage

def upload_csv_to_bigquery(
    project:str,
    dataset:str,
    table:str,
    local_path:str,
    dtype=None
    ):

    t = f"{project}.{dataset}.{table}"
    df = pd.read_csv(local_path + f"/{table}.csv", dtype=dtype)

    client = bigquery.Client()

    write_mode = "WRITE_TRUNCATE"
    job_config = bigquery.LoadJobConfig(write_disposition=write_mode)

    job = client.load_table_from_dataframe(df, t, job_config=job_config)
    result = job.result()

def upload_to_cloud_platform(
    project:str,
    dataset:str,
    table:str,
    local_path:str,
    dtype=None
    ):

    t = f"{project}.{dataset}.{table}"
    df = pd.read_csv(local_path + f"/{table}.csv", dtype=dtype)

    client = bigquery.Client()

    write_mode = "WRITE_TRUNCATE"
    job_config = bigquery.LoadJobConfig(write_disposition=write_mode)

    job = client.load_table_from_dataframe(df, t, job_config=job_config)
    result = job.result()

def get_data_bigquery(
        gcp_project:str,
        query:str,
        cache_path:Path,
        data_has_header=True
    ) -> pd.DataFrame:

    if cache_path.is_file():
        df = pd.read_csv(cache_path, header='infer' if data_has_header else None)

    else:
        client = bigquery.Client(project=gcp_project)
        query_job = client.query(query)
        result = query_job.result()
        df = result.to_dataframe()

        if df.shape[0] > 1:
            df.to_csv(cache_path, header=data_has_header, index=False)

    return df

def get_data_cloud_platform(
        gcp_project:str,
        query:str,
        cache_path:Path,
        data_has_header=True
    ) -> pd.DataFrame:

    if cache_path.is_file():
        df = pd.read_csv(cache_path, header='infer' if data_has_header else None)

    else:
        client = bigquery.Client(project=gcp_project)
        query_job = client.query(query)
        result = query_job.result()
        df = result.to_dataframe()

        if df.shape[0] > 1:
            df.to_csv(cache_path, header=data_has_header, index=False)

    return df
