import os
import json
from datetime import datetime
from google.cloud import storage

def save_response_json_gcs(data):
    # client = storage.Client()
    # bucket_name = os.getenv("RAW_DATA_BUCKET")
    # bucket = client.bucket(bucket_name)

    # now = datetime.now()
    # blob_path = "{api_name}/{year}/{month}/{day}/{api_name}_{tz}.json".format(
    #     api_name = "muni_data",
    #     year = now.year,
    #     month = now.month,
    #     day = now.day,
    #     tz = now.isoformat()
    # )

    # blob = bucket.blob(blob_path)
    # blob.upload_from_string(json.dumps(data), content_type="application/json")

    # print(f" Saved raw JSON to gs://{bucket_name}/{blob_path}")
    pass