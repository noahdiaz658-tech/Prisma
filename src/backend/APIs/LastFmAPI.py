import json
import src.backend.helpers as helpers

class LastFmClient:

    def __init__(self):
        self.API_KEY = helpers.LASTFM_API_KEY
        self.EMAIL_ADDRESS = helpers.EMAIL_ADDRESS
        self.BASE_URL = "http://ws.audioscrobbler.com/2.0/"
        self.REQUEST_HEADER = {"User-Agent": f"Prisma ({self.EMAIL_ADDRESS})"}
        self.METADATA_DIR = "../cache/temp/artist_metadata"
        self.LASTFM_USERNAME = "noahdiaz658"

    def search_album(self, artist:str , album_name: str):

        response = helpers.request_helper(
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

        response = helpers.request_helper(self.BASE_URL, parameters ,self.REQUEST_HEADER)

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

        response = helpers.request_helper(
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

        response = helpers.request_helper(
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

        response = helpers.request_helper(
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
