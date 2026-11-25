from dotenv import load_dotenv
load_dotenv()

import time
from pathlib import Path

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

def resolve_image_url(media_directory):

    artist = Path(media_directory).resolve().stem

    media_cache_directory = Path(f"../cache/media/artist_images/{artist}")

    media_cache_directory.mkdir(exist_ok = True)

    with open (media_directory, "r") as file:
        artist_metadata = json.load(file)

    for image_type, image_url in dict(artist_metadata["media"]).items():
        response = requests.get(image_url)

        with open(f"../cache/media/artist_images/{artist}/{image_type}.png", "wb") as file:
            file.write(response.content)

resolve_image_url("../cache/temp/artist_metadata/Rauw Alejandro.json")