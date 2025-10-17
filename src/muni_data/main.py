import json
from muni_data.etl.extract import fetch_api_data
from muni_data.etl.transform import transform_to_dataframe
from muni_data.etl.load import load_to_bigquery, save_response_json_gcs
from muni_data.etl.utils import log_info
import traceback

def main(request=None):
    try:
        log_info("Starting the pipeline")

        # Step 1: Extract
        response_data_bytes = fetch_api_data()
        response_decoded_string = response_data_bytes.decode('utf-8-sig')
        data = json.loads(response_decoded_string)
        log_info("Fetched data from API")

        # Step 2: Backup raw data to Cloud Storage
        save_response_json_gcs(data)
        log_info("Raw data saved to GCS")

        # Step 3: Transform
        df = transform_to_dataframe(data)
        log_info(f"Transformed data into dataframe with {len(df)} rows")

        # Step 4: Load
        load_to_bigquery(df)
        log_info("Data loaded to BigQuery successfully")

        return ("Success", 200)

    except Exception as e:
        log_info(f"Error: {str(e)}\n{traceback.format_exc()}")
        return ("Failed", 500)