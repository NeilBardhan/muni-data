import os
import requests
from dotenv import load_dotenv
from .utils import log_info

load_dotenv()

def fetch_api_data():
    api_key = os.getenv("MUNI_API_KEY")
    api_url = os.getenv("API_URL")
    api_url = "{}{}".format(api_url, api_key)
    # headers = {
    #     "Authorization": f"Bearer {os.getenv('MUNI_API_KEY')}"
    # }
    # response = requests.get(api_url, headers=headers, timeout=30)
    response = requests.get(api_url)
    response.raise_for_status()

    log_info("API call successful")
    return response.content
