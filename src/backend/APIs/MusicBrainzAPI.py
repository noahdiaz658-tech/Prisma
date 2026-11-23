import src.backend.helpers as helpers
import json, time

class MusicBrainzClient:

    def __init__(self):
        self.BASE_URL = "https://musicbrainz.org/ws/2"
        #PrismaMusic/v0.1
        self.REQUEST_HEADER = {"User-Agent": f"PrismaMusic/v0.1 ({helpers.EMAIL_ADDRESS})"}
        self.ARTIST_METADATA_DIRECTORY = "../cache/temp/artist_metadata"

        self.artist = ""

    def search_artist(self, artist: str):
        self.artist = artist

        response = helpers.request_helper(f"{self.BASE_URL}/artist", {"query": f"artist:{self.artist}", "fmt": "json"}, self.REQUEST_HEADER)

        response_data = helpers.safe_json(response)

        if response:
            artists = response_data.get('artists')

        if not artists:
            print("No artists found")
            print(response_data)
            return None

        MBID = response_data['artists'][0]['id']

        artist_metadata = {
                "mbid": MBID,
                "artist": self.artist
        }

        with open(f"{self.ARTIST_METADATA_DIRECTORY}/{artist}.json", "w") as file:
            json.dump(artist_metadata, file, indent = 4)

        return MBID

    def get_artist(self, mbid):

        response = helpers.request_helper(f"{self.BASE_URL}/artist/{mbid}", {"fmt": "json"}, self.REQUEST_HEADER)
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
            response = helpers.request_helper(
            f"{self.BASE_URL}/release-group",
                {
                    "artist": mbid,
                    "limit": 100,
                    "offset": offset,
                    "fmt": "json"
                },
                self.REQUEST_HEADER
            )

            response_data = helpers.safe_json(response)

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

