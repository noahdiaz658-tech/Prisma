import json, time
import src.backend.helpers as helpers

class DeezerClient:

    def __init__(self):
        self.BASE_URL = "https://api.deezer.com"
        self.ARTIST_METADATA_DIRECTORY = "../cache/temp/artist_metadata"
        self.DEEZER_GENRES_PATH = "../cache/DeezerGenres.json"

    def search_artist(self, artist):

        response = helpers.request_helper(
            f"{self.BASE_URL}/search/artist",
            {
                "q": artist,
                "limit": 5
            },
            "")

        possible_artists = {}

        # Enumerates all artists in response results
        for index, possible_artist in enumerate(response.json()["data"]):
            possible_artists[index] = possible_artist["nb_fan"]

        # Sorts each artist's index by their fans
        possible_artists = dict(sorted(possible_artists.items(), key = lambda item:item[1], reverse=True))

        # Gets artist with most fans to avoid false search result
        corrected_artist_index = next(iter(possible_artists))

        json_response = helpers.safe_json(response)
        json_response = json_response["data"][corrected_artist_index]

        with open(f"{self.ARTIST_METADATA_DIRECTORY}/{artist}.json", "r") as file:
            artist_metadata = json.load(file)

        if not "artist" in artist_metadata:
            artist_metadata["artist"] = json_response["name"]

        artist_metadata["deezer-id"] =  json_response["id"]
        artist_metadata["media"] = {}
        artist_metadata["media"]["deezer-artist-image"] = json_response["picture_big"]


        with open(f"{self.ARTIST_METADATA_DIRECTORY}/{artist}.json", "w") as file:
            json.dump(artist_metadata, file, indent=4)

    def get_artist_albums(self, artist):

        with open(f"{self.ARTIST_METADATA_DIRECTORY}/{artist}.json", "r") as file:
            artist_metadata = json.load(file)

        with open(self.DEEZER_GENRES_PATH, "r") as file:
            deezer_genres = json.load(file)

        deezer_genres_checksum = deezer_genres.copy()

        deezer_id = artist_metadata["deezer-id"]

        response = helpers.request_helper(f"{self.BASE_URL}/artist/{deezer_id}/albums", {"limit": 200}, "")

        json_response = helpers.safe_json(response)
        json_response = json_response["data"]

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
                "media": {
                    "deezer-album-image": album["cover_big"],
                }
                }
            )

            if not any(
                item["genre_id"] == album["genre_id"]
                for item in deezer_genres
            ):
                deezer_genres.append(
                    {
                        "genre_id": album["genre_id"],
                        "genre": None,
                        "image": None
                    }
                )


        with open(f"{self.ARTIST_METADATA_DIRECTORY}/{artist}.json", "w") as file:
            json.dump(artist_metadata, file, indent=4)

        if not deezer_genres == deezer_genres_checksum:
            with open(self.DEEZER_GENRES_PATH, "w") as file:
                json.dump(deezer_genres, file, indent=4)

    def get_similar_artists(self, artist):
        with open(f"{self.ARTIST_METADATA_DIRECTORY}/{artist}.json", "r") as file:
            artist_metadata = json.load(file)

        deezer_id = artist_metadata["deezer-id"]

        response = helpers.request_helper(f"{self.BASE_URL}/artist/{deezer_id}/related", "", "")

        json_response = helpers.safe_json(response)
        json_response = json_response["data"]
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

        response = helpers.request_helper(f"{self.BASE_URL}/artist/{deezer_id}/top", {"limit": 5}, "")

        print(response.json())

    def get_artist_radio(self, artist):

        with open(f"{self.ARTIST_METADATA_DIRECTORY}/{artist}.json", "r") as file:
            artist_metadata = json.load(file)

        deezer_id = artist_metadata["deezer-id"]

        response = helpers.request_helper(f"{self.BASE_URL}/artist/{deezer_id}/radio", "", "")
        print(response.json())

    def resolve_genres(self):

        with open(self.DEEZER_GENRES_PATH, "r") as file:
            genres_data = json.load(file)

        for genre in genres_data:
            response = helpers.request_helper(f"{self.BASE_URL}/genre/{genre["genre_id"]}", "", "")

            json_response = helpers.safe_json(response)

            if not "error" in json_response:
                genre["genre"] = json_response["name"]
                genre["image"] = json_response["picture_xl"]
            else:
                print(f"ERROR - {json_response["error"]["message"]} Code {json_response["error"]["code"]} (Most likely non-existant genre id)")
            time.sleep(5)

        with open(self.DEEZER_GENRES_PATH, "w") as file:
            json.dump(genres_data, file, indent=4)