# UPLOAD TABLE

from google.cloud import bigquery
import pandas as pd

PROJECT = "filmaholic-398017"
DATASET = "filmaholic"
TABLE = "<TABLE_NAME>"

table = f"{PROJECT}.{DATASET}.{TABLE}"
df = pd.read_csv("raw_data/<TABLE_NAME>.csv")

client = bigquery.Client()

write_mode = "WRITE_TRUNCATE"
job_config = bigquery.LoadJobConfig(write_disposition=write_mode)

job = client.load_table_from_dataframe(df, table, job_config=job_config)
result = job.result()


####################################

#LOAD TABLE

from google.cloud import bigquery
import pandas as pd

PROJECT = "filmaholic-398017"
DATASET = "filmaholic"
TABLE = "<TABLE_NAME>"

query = f"""
    SELECT *
    FROM {PROJECT}.{DATASET}.{TABLE}
    """

client = bigquery.Client(project=gcp_project)
query_job = client.query(query)
result = query_job.result()
df = result.to_dataframe()
