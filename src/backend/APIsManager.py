from time import sleep
from dotenv import load_dotenv
load_dotenv()

import requests, json, os, time
import requests.api

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")

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
            time.sleep(2.5 * attempt)

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
        #PrismaMusic/v0.1
        self.REQUEST_HEADER = {"User-Agent": f"PrismaMusic/v0.1 ({EMAIL_ADDRESS})"}
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

    def get_MBIB(self, artist):

        with open(f"{self.ARTIST_METADATA_DIRECTORY}/{artist}.json", "r") as file:
            artist_metadata = json.load(file)
        MBID = artist_metadata["mbid"]
        return MBID

    def get_artist_albums(self, artist, mbid):

        offset = 0
        all_release_groups = []

        album_metadata = []
        ep_metadata = []
        single_metadata = []

        excluded_secondary_types = {
            "Compilation",
            "Live",
            "Interview",
            "Soundtrack",
            "Demo"
        }

        # Continues searching until all results are found
        while True:
            response = request_helper(
            f"{self.BASE_URL}/release-group",
                {
                    "artist": mbid,
                    "limit": 100,
                    "offset": offset,
                    "fmt": "json"
                },
                self.REQUEST_HEADER
            )

            response_data = safe_json(response)

            # Iterates through releases in response
            for release in response_data["release-groups"]:

                # Release type filtering
                if release["primary-type"] in [
                    "Album",
                    "EP",
                    "Single"
                ] and not excluded_secondary_types.intersection(
                    release["secondary-types"]
                ):
                    if release["primary-type"] == "Album":
                        album_metadata.append(
                            {
                                "mbid": release.get("id"),
                                "title": release.get("title"),
                                "first-release-date": release.get('first-release-date'),
                                "primary-type": release.get("primary-type"),
                                "secondary-types": release.get("secondary-types", [])
                            }
                        )
                    elif release["primary-type"] == "EP":
                        ep_metadata.append(
                            {
                                "mbid": release.get("id"),
                                "title": release.get("title"),
                                "first-release-date": release.get('first-release-date'),
                                "primary-type": release.get("primary-type"),
                                "secondary-types": release.get("secondary-types", [])
                            }
                        )
                    else:
                        single_metadata.append(
                            {
                                "mbid": release.get("id"),
                                "title": release.get("title"),
                                "first-release-date": release.get('first-release-date'),
                                "primary-type": release.get("primary-type"),
                                "secondary-types": release.get("secondary-types", [])
                            }
                        )

            release_groups = response_data["release-groups"]
            all_release_groups.extend(release_groups)

            # Breaks if all releases have been processed
            if len(all_release_groups) >= response_data["release-group-count"]:
                break

            # Increases search offset
            offset += 100

            # Delay for API
            time.sleep(4)

        with open(f"{self.ARTIST_METADATA_DIRECTORY}/{artist}.json", "r") as file:
            artist_metadata = json.load(file)

        artist_metadata["albums"] = album_metadata
        artist_metadata["eps"] = ep_metadata
        artist_metadata["singles"] = single_metadata

        with open(f"{self.ARTIST_METADATA_DIRECTORY}/{artist}.json", "w") as file:
            json.dump(artist_metadata, file, indent=4)

class LastFmClient:

    def __init__(self):
        self.API_KEY = os.getenv("LASTFM_API_KEY")
        self.EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
        self.BASE_URL = "http://ws.audioscrobbler.com/2.0/"
        self.REQUEST_HEADER = {"User-Agent": f"Prisma ({self.EMAIL_ADDRESS})"}
        self.METADATA_DIR = "../cache/temp/artist_metadata"
        self.LASTFM_USERNAME = "noahdiaz658"

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

        # Loads artist metadata
        with open(f"../cache/temp/artist_metadata/{artist}.json", "r") as file:
            releases_metadata = json.load(file)

        # Enumerates list of albums for artist
        for index, album in enumerate(releases_metadata["albums"]):
            if album["title"] == album_name:
                releases_metadata["albums"][index]["playcount"] = json_response["playcount"]

                # Gets largest available image
                releases_metadata["albums"][index]["image"] = json_response["image"][len(json_response["image"]) - 1]["#text"]

                json_response_tracks = json_response["tracks"]["track"]
                releases_metadata["albums"][index]["tracks"] = []

                for track in json_response_tracks:
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

    def add_top_tags(self, artist:str, album_name:str, method:str):

        if method == "artist":
            parameters = {
                "method": "artist.gettoptags",
                "artist": artist,
                "autocorrect": 1,
                "api_key": self.API_KEY,
                "format": "json"
            }
        elif method == "album":
            parameters = {
                "method": "album.gettoptags",
                "artist": artist,
                "album": album_name,
                "autocorrect": 1,
                "api_key": self.API_KEY,
                "format": "json"
            }

        response = request_helper(self.BASE_URL, parameters ,self.REQUEST_HEADER)

        # Checks for API request error NOT connection errors
        if not "error" in response.json():

            # Variable name helper
            json_response = response.json()["toptags"]

            # Checks if the tag list is empty
            if not json_response["tag"] == []:
                print(json_response)

                # Loads album metadata
                with open(f"{self.METADATA_DIR}/{artist}.json", "r") as file:
                    releases_metadata = json.load(file)

                # Checks request method
                if method == "artist":

                    # Creates empty list key for artist tags
                    releases_metadata["artist-tags"] = []

                    for tag in json_response["tag"]:
                        releases_metadata["artist-tags"].append(tag["name"])

                elif method == "album":

                    # Enumerates all albums for the artist
                    for index, album in enumerate(releases_metadata["albums"]):
                        # Locates desired album using metadata
                        if album["title"] == album_name:

                            # Creates empty list key for album tags
                            releases_metadata["albums"][index]["album-tags"] = []

                            # Appends all tags to metadata
                            for tag in json_response["tag"]:
                                releases_metadata["albums"][index]["album-tags"].append(tag["name"])

                # Writes additions to disk
                with open(f"{self.METADATA_DIR}/{artist}.json", "w") as file:
                    json.dump(releases_metadata, file, indent=4)
            else:
                print("ERROR - No tags found")
        else:
            print(f"ERROR - {response.json()["message"]}")

    def get_similar_artists(self, artist:str):

        response = request_helper(
            self.BASE_URL,
            {
                "method": "artist.getsimilar",
                "limit": 30,
                "artist": artist,
                "autocorrect": 1,
                "api_key": self.API_KEY,
                "format": "json"
            },
            self.REQUEST_HEADER
        )

        print(response.json())

        if not "error" in response.json():
            json_response = response.json()["similarartists"]["artist"]

            with open(f"{self.METADATA_DIR}/{artist}.json", "r") as file:
                artist_metadata = json.load(file)

            artist_metadata["similar-artists"] = []

            for similar_artist in json_response:
                artist_metadata["similar-artists"].append(
                    {
                        "mbid": similar_artist.get("mbid", "no_mbid_from_last.fm"),
                        "artist": similar_artist["name"],
                        "match-coefficient": similar_artist["match"]
                    }
                )

            with open(f"{self.METADATA_DIR}/{artist}.json", "w") as file:
                json.dump(artist_metadata, file, indent=4)

        else:
            print(f"ERROR - {response.json()["message"]}")

    # Not production ready
    def get_artist_albums(self, artist, mbid):

        response_page = 1

        response = request_helper(
            self.BASE_URL,
            {
                "method": "artist.gettopalbums",
                "artist": artist,
                "autocorrect": 1,
                "page": response_page,
                "limit": 700,
                "api_key": self.API_KEY,
                "format": "json"

            },
            self.REQUEST_HEADER
        )

        json_response = response.json()["topalbums"]["album"]

        with open("test.json", "r") as file:
            data = json.load(file)

        data["albums"] = []

        for album in json_response:
            data["albums"].append(
                {
                    "mbid": album.get("mbid", "no_mbid_from_last.fm"),
                    "name": album["name"],
                    "playcount": album.get("playcount", "unknown"),
                    "popularity-rank": album["@attr"].get("rank", "unknown")
                }
            )


        with open("test.json", "w") as file:
            json.dump(data,file,indent=4)

        print(response.json())
        print(len(json_response))

    def get_top_artists_chart(self):

        response = request_helper(
            self.BASE_URL,
            {
                "method": "chart.gettopartists",
                "page": 1,
                "limit": 100,
                "api_key": self.API_KEY,
                "format": "json"
            },
            self.REQUEST_HEADER
        )

        print(response.json())

class DeezerClient:

    def __init__(self):
        self.BASE_URL = "https://api.deezer.com"
        self.REQUEST_HEADER = {"User-Agent": f"PrismaMusic/v0.1 ({EMAIL_ADDRESS})"}
        self.ARTIST_METADATA_DIRECTORY = "../cache/temp/artist_metadata"

    def search_artist(self, artist):

        response = request_helper(f"{self.BASE_URL}/search/artist", {"q": artist}, "")

        json_response = response.json()["data"][0]

        with open(f"{self.ARTIST_METADATA_DIRECTORY}/{artist}.json", "r") as file:
            artist_metadata = json.load(file)

        if not "artist" in artist_metadata:
            artist_metadata["artist"] = json_response["name"]

        artist_metadata["deezer-id"] =  json_response["id"]
        artist_metadata["image"] = json_response["picture_big"]

        with open(f"{self.ARTIST_METADATA_DIRECTORY}/{artist}.json", "w") as file:
            json.dump(artist_metadata, file, indent=4)

    def get_artist_albums(self, artist):

        with open(f"{self.ARTIST_METADATA_DIRECTORY}/{artist}.json", "r") as file:
            artist_metadata = json.load(file)

        deezer_id = artist_metadata["deezer-id"]

        response = request_helper(f"{self.BASE_URL}/artist/{deezer_id}/albums", {"limit": 200}, "")

        json_response = response.json()["data"]

        artist_metadata["releases"] = {}
        artist_metadata["releases"]["albums"] = []
        artist_metadata["releases"]["eps"] = []
        artist_metadata["releases"]["singles"] = []

        for album in json_response:

            if album["record_type"] == "album":
                collection_type = "album"
            elif album["record_type"].lower() == "ep":
                collection_type = "ep"
            else:
                collection_type = "single"

            artist_metadata["releases"][f"{collection_type}s"].append(
                {
                "deezer-id": album["id"],
                "deezer-genre-id": album["genre_id"],
                "title": album["title"],
                "release-data": album["release_date"],
                "explicit": album["explicit_lyrics"],
                "type": album["record_type"],
                "image": album["cover_big"],
                }
            )

        with open(f"{self.ARTIST_METADATA_DIRECTORY}/{artist}.json", "w") as file:
            json.dump(artist_metadata, file, indent=4)

    def get_similar_artists(self, artist):
        with open(f"{self.ARTIST_METADATA_DIRECTORY}/{artist}.json", "r") as file:
            artist_metadata = json.load(file)

        deezer_id = artist_metadata["deezer-id"]

        response = request_helper(f"{self.BASE_URL}/artist/{deezer_id}/related", "", "")

        json_response = response.json()["data"]
        artist_metadata["deezer-similar-artists"] = []

        for similar_artist in json_response:
            artist_metadata["deezer-similar-artists"].append(
                {
                    "deezer-id": similar_artist["id"],
                    "artist": similar_artist["name"],
                    "image": similar_artist["picture_big"],
                }
            )

        with open(f"{self.ARTIST_METADATA_DIRECTORY}/{artist}.json", "w") as file:
            json.dump(artist_metadata, file, indent=4)

    def get_top_songs(self, artist):
        with open(f"{self.ARTIST_METADATA_DIRECTORY}/{artist}.json", "r") as file:
            artist_metadata = json.load(file)

        deezer_id = artist_metadata["deezer-id"]

        response = request_helper(f"{self.BASE_URL}/artist/{deezer_id}/top", {"limit": 5}, "")

        print(response.json())

Lclient = LyricsClient()
MBClient = MusicBrainzClient()
FMClient = LastFmClient()
DZClient = DeezerClient()
#Artist_MBID = MBClient.get_MBIB("Radiohead")
#MBClient.get_artist_albums("Radiohead", MBClient.get_MBIB("Radiohead"))
#FMClient.search_albums("Radiohead", "OK Computer")
#FMClient.add_top_album_tags("Radiohead", "OK Computer", "artist")
#FMClient.get_similar_artists("Cris MJ")
#FMClient.get_top_artists_chart()

DZClient.search_artist("Bad Bunny")
time.sleep(3)
DZClient.get_artist_albums("Bad Bunny")
time.sleep(3)
DZClient.get_similar_artists("Bad Bunny")
time.sleep(3)
DZClient.get_top_songs("Bad Bunny")

"""
image_response = requests.get("https://lastfm-img.freetls.fastly.net/i/u/34s/2a96cbd8b46e442fc41c2b86b821562f.png")
with open("test.png", "wb") as pic:
    pic.write(image_response.content)
"""