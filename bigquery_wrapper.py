import geojson

from google.cloud import bigquery
from google.oauth2.service_account import Credentials


class BigQueryWrapper:
    def __init__(self, project_id, dataset_id, table_id, cred_file):
        credentials = Credentials.from_service_account_file(cred_file)
        self.bigquery_client = bigquery.Client(
            project=project_id, 
            credentials=credentials)
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id
  

    def get_bigquery_max_timestamp(self):
        query = f"""
            SELECT
              UNIX_SECONDS(MAX(timestamp)) AS max_timestamp
            FROM
              `{self.project_id}.{self.dataset_id}.{self.table_id}`
        """
        query_job = self.bigquery_client.query(query)
        results = query_job.result()
        for row in results:
            return int(row.max_timestamp) or 0

    def upload_to_bigquery(self, rows):
        """
        rows - A list of dictionaries with timestamp, longitude and latitude
        """
        records = [
            {
                "timestamp": row["timestamp"],
                "coordinates": geojson.dumps(
                    geojson.Point(
                        (
                            float(row["longitude"]),
                            float(row["latitude"]),
                        )
                    )
                ),
            }
            for row in rows
        ]

        errors = self.bigquery_client.insert_rows_json(
             f"{self.project_id}.{self.dataset_id}.{self.table_id}", 
              records
        )
        if errors:
            raise RuntimeError(f"row insert failed: {errors}")

        return records