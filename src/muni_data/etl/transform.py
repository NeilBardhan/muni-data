import json
import pandas as pd
from datetime import datetime

def transform_to_dataframe(data):
    df = pd.DataFrame(data)
    df = df.rename(columns = {"Id": "system_id", "Name": "system_name", "LastGenerated": "last_generated"}, errors = "raise")
    df['ingestion_time'] = datetime.now()
    return df