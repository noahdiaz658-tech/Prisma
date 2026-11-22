from dotenv import load_dotenv
load_dotenv()

import time

import requests
import json, os

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")

def json_to_lrc(json_path, lrc_path):

    with open(json_path, "r") as file:
        json_data = json.load(file)

    with open(lrc_path, "w") as file:
        file.write(json_data["syncedLyrics"])

def safe_json(response):

    try:
        return response.json()

    except Exception as exception:
        print("JSON Error: ", exception)
        return None

def request_helper(endpoint, parameters, header):
    MAX_RETRIES = 3
    attempt = 1

    while attempt < MAX_RETRIES:

        response = requests.get(endpoint, params=parameters, headers=header)

        if response.status_code == 200:
            print(f"Request to {response.url} for {parameters} successful.")
            return response
        elif response.status_code == 404:
            print(f"ERROR - Endpoint url not found.")
            return None
        elif response.status_code == 503:
            print(f"ERROR - Server Timeout")
            time.sleep(2.5 * attempt)

        print("Retrying...")
        attempt += 1

    return None