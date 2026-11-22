import json
import src.backend.helpers as helpers

class LrcLibClient:

    def __init__(self):

        # DON'T TOUCH - Altering will result in lower rate limits and possible errors
        APP_ID = "7YP3KzZFees1XVCC1qrR3DRIBRYC0aPZWGDCqk33DPQ"

        self.BASE_URL = "https://lrclib.net/api/get"
        self.LYRICS_DIRECTORY = "../cache/lyrics"


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

        response = helpers.request_helper(self.BASE_URL, self.parameters, "")

        if response.status_code == 200:
            print(f"DEBUG: Successfully fetched song lyrics for [{track_name} by {artist_name}]")
            with open("../cache/temp/Temp_Lyrics.json", "w") as file:
                json.dump(response.json(), file, indent=4)
            helpers.json_to_lrc("../../cache/temp/Temp_Lyrics.json", f"{self.LYRICS_DIRECTORY}/{track_name}.lrc")
        else:
            print(f"ERROR: {response.text}")