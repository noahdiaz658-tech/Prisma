from time import sleep
from dotenv import load_dotenv
load_dotenv()

import requests, json, os, time
import requests.api

# Other params: "album_name", "duration", or just "id"
"""
response = requests.get("https://lrclib.net/api/search", params = {
    "q": song_title
})
"""

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
            time.sleep(2 * attempt)

        print("Retrying...")
        attempt += 1

    return None




class LyricsClient:

    def __init__(self):

        # DON'T TOUCH - Altering will result in lower rate limits and possible errors
        APP_ID = "7YP3KzZFees1XVCC1qrR3DRIBRYC0aPZWGDCqk33DPQ"

        self.BASE_URL = "https://lrclib.net/api/get"

        self.parameters = {
            "track_name": "",
            "artist_name": "",
            "album_name": "",
            "Lrclib-App-Id": APP_ID,
        }

    def fetch_lyrics(self, track_name: str, artist_name: str, album_name: str):

        self.parameters["track_name"] = track_name
        self.parameters["artist_name"] = artist_name
        self.parameters["album_name"] = album_name

        response = request_helper(self.BASE_URL, self.parameters, "")

        if response.status_code == 200:
            print(f"DEBUG: Successfully fetched song lyrics for [{track_name} by {artist_name}]")
            with open("../cache/temp/Temp_Lyrics.json", "w") as file:
                json.dump(response.json(), file, indent=4)
        else:
            print(f"ERROR: {response.text}")

class MusicBrainzClient:

    def __init__(self):
        self.BASE_URL = "https://musicbrainz.org/ws/2"
        self.REQUEST_HEADER = {"User-Agent": "PrismaMusic/0.1 (noahdiaz658@gmail.com)"}
        self.ARTIST_METADATA_DIRECTORY = "../cache/temp/artist_metadata"

        self.artist = ""

    def search_artist(self, artist: str):
        self.artist = artist

        response = request_helper(f"{self.BASE_URL}/artist", {"query": f"artist:{self.artist}", "fmt": "json"}, self.REQUEST_HEADER)

        response_data = safe_json(response)

        if response:
            artists = response_data.get('artists')

        if not artists:
            print("No artists found")
            print(response_data)
            return None

        MBID = response_data['artists'][0]['id']

        artist_metadata = {
                "mbid": MBID,
                "artist": self.artist,
                "albums": []
        }

        with open(f"{self.ARTIST_METADATA_DIRECTORY}/{artist}.json", "w") as file:
            json.dump(artist_metadata, file, indent = 4)

        return MBID

    def get_artist(self, mbid):

        response = request_helper(f"{self.BASE_URL}/artist/{mbid}", {"fmt": "json"}, self.REQUEST_HEADER)
        print(response.json())

    def get_MBIB(self):

        with open(f"{self.ARTIST_METADATA_DIRECTORY}/{self.artist}.json", "r") as file:
            artist_metadata = json.load(file)
        MBID = artist_metadata[self.artist]["mbid"]
        return MBID


    def get_artist_album(self, mbid):

        response = request_helper(f"{self.BASE_URL}/release-group", {"artist": mbid, "fmt": "json"}, self.REQUEST_HEADER)
        response_data = safe_json(response)

        print(response_data)

        releases_metadata = []
        for release in response_data["release-groups"]:
            releases_metadata.append(
                {
                    "mbid": release.get("id"),
                    "title": release.get("title"),
                    "first-release-date": release.get('first-release-date'),
                    "primary-type": release.get("primary-type"),
                    "secondary-types": release.get("secondary-types", [])
                }
            )



        with open(f"{self.ARTIST_METADATA_DIRECTORY}/{self.artist}.json", "r") as file:
            artist_metadata = json.load(file)

        artist_metadata["albums"] = releases_metadata

        with open(f"{self.ARTIST_METADATA_DIRECTORY}/{self.artist}.json", "w") as file:
            json.dump(artist_metadata, file, indent=4)


        print(response.url)
        print(response.json())

class LastFmClient:

    def __init__(self):
        self.API_KEY = os.getenv("LASTFM_API_KEY")
        self.BASE_URL = "http://ws.audioscrobbler.com/2.0/"
        self.REQUEST_HEADER = {"User-Agent": "Prisma (noahdiaz658@gmail.com)"}

    def search_album(self, artist:str , album_name: str):

        response = request_helper(
            self.BASE_URL,
            {
                "method": "album.getinfo",
                "api_key": self.API_KEY,
                "artist": artist,
                "album": album_name,
                "format": "json"
            },
            self.REQUEST_HEADER
        )

        releases_metadata = []
        json_response = response.json()["album"]

        with open(f"../cache/temp/artist_metadata/{artist}.json", "r") as file:
            releases_metadata = json.load(file)

        for index, album in enumerate(releases_metadata["albums"]):
            if album["title"] == album_name:
                releases_metadata["albums"][index]["playcount"] = json_response["playcount"]

                # Gets largest available image
                releases_metadata["albums"][index]["image"] = json_response["image"][len(json_response["image"]) - 1]["#text"]

                json_response_tracks = json_response["tracks"]["track"]
                releases_metadata["albums"][index]["tracks"] = []

                for track_index, track in enumerate(json_response_tracks):
                    releases_metadata["albums"][index]["tracks"].append(
                    {
                        "title": track["name"],
                        "artists": track["artist"]["name"],
                        "duration": track["duration"]
                    }
                    )

        with open(f"../cache/temp/artist_metadata/{artist}.json", "w") as file:
            json.dump(releases_metadata, file, indent = 4)

        print(response.json())

    def add_album_tags(self, artist:str, album_name: str):

"""
def load_artist_mbid(artist):
    with open(f"{self.ARTIST_METADATA_DIRECTORY}/{artist}.json", "r") as file:
        return(json.load(file)[artist]["mbid"])
"""


FMClient = LastFmClient()
FMClient.search_album("Cris MJ", "Partyson")
"""
Lclient = LyricsClient()

MBClient = MusicBrainzClient()

Artist_MBID = MBClient.search_artist("Yandel")

Lclient.fetch_lyrics("Si No Es Contigo", "Cris MJ", "")
json_to_lrc("../cache/temp/Temp_Lyrics.json", "../cache/temp/Temp_Lyrics.lrc")

if Artist_MBID:
    time.sleep(2.5)
    MBClient.get_artist(Artist_MBID)
    time.sleep(2)
    MBClient.get_artist_album(Artist_MBID)
"""