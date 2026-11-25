import json
import src.backend.helpers as helpers

class AudioDbClient:

    def __init__(self):
        # Free API key
        self.API_KEY = "123"
        self.BASE_URL = f"https://www.theaudiodb.com/api/v1/json/{self.API_KEY}"
        self.ARTIST_METADATA_DIRECTORY = "../cache/temp/artist_metadata"

    def search_artist(self, artist:str):

        response = helpers.request_helper(f"{self.BASE_URL}/search.php", {"s": artist}, "")
        desired_tags_dict = {
            "audiodb-id": "idArtist",
            "year-started": "intFormedYear",
            "year-born": "intBornYear",
            "year-died": "intDiedYear",
            "followers": "intFollowers",
            "popularity-percentage": "intPopularity",
            "style": "strStyle",
            "audiodb-genre": "strGenre",
            "mood": "strMood",
            "bio": "strBiography",
            "gender": "strGender",
            "aritst-label-company": "strLabel",
            "label-company-audiodb-id": "idLabel",
            "members": "intMembers",
            "origin": "strCountry",
            "origin-country": "strCountryCode",
            "artist-thumbnail": "strArtistThumb",
            "artist-logo": "strArtistLogo",
            "artist-cutout": "strArtistCutout",
            "aritst-clear-art": "strArtistClearart",
            "artist-wide-thumbnail": "strArtistWideThumb",
            "fan-art-1": "strArtistFanart",
            "fan-art-2": "strArtistFanart2",
            "fan-art-3": "strArtistFanart3",
            "fan-art-4": "strArtistFanart4",
            "artist-banner": "strArtistBanner",
        }
        desired_tags_aliases = desired_tags_dict.keys()
        image_tags = [
            "strArtistThumb",
            "strArtistLogo",
            "strArtistCutout",
            "strArtistClearart",
            "strArtistWideThumb",
            "strArtistFanart",
            "strArtistFanart2",
            "strArtistFanart3",
            "strArtistFanart4",
            "strArtistBanner",
        ]

        print(response.json())
        try:
            with open(f"{self.ARTIST_METADATA_DIRECTORY}/{artist}.json", "r") as file:
                artist_metadata = json.load(file)
        except FileNotFoundError:
            print(f"ERROR file {self.ARTIST_METADATA_DIRECTORY}/{artist}.json not found. (Most likely misspelled artist name)")
            return

        if response.json()["artists"] is None:
            print("ERROR - Artist not found.")
            artist_metadata["no-audiodb-metadata"] = True
        else:
            json_response = helpers.safe_json(response)["artists"][0]
            artist_metadata["no-audiodb-metadata"] = False

        if "media" not in artist_metadata:
            artist_metadata["media"] = {}

        for tag_alias in desired_tags_aliases:
            if desired_tags_dict[tag_alias] in image_tags:
                if not json_response.get(desired_tags_dict[tag_alias], None) is None and not json_response.get(desired_tags_dict[tag_alias], None) == "":
                    artist_metadata["media"][tag_alias] = json_response.get(desired_tags_dict[tag_alias], "N/A")
            else:
                if not json_response.get(desired_tags_dict[tag_alias], None) is None and not json_response.get(desired_tags_dict[tag_alias], None) == "":
                    artist_metadata[tag_alias] = json_response.get(desired_tags_dict[tag_alias], "N/A")


        with open(f"{self.ARTIST_METADATA_DIRECTORY}/{artist}.json", "w") as file:
            json.dump(artist_metadata, file, indent=4)

    def search_album(self, artist:str, album:str):

        desired_tags_dict = {
            "mbid": "strMusicBrainzID",
            "audiodb-id": "idAlbum",
            "audiodb-genre": "strGenre",
            "album-label-company": "strLabel",
            "label-company-audiodb-id": "idLabel",
            "album-thumbnail": "strAlbumThumb",
            "album-back": "strAlbumBack",
            "album-cd-art": "strAlbumCDart",
            "album-spine": "strAlbumSpine",
            "album-3d-case": "strAlbum3DCase",
            "album-3d-flat": "strAlbum3DFlat",
            "album-3d-face": "strAlbum3DFace",
            "album-3D-thumbnail": "strAlbum3DThumb",
            "description": "strDescription",
            "popularity-percentage": "intPopularity",
            "mood": "strMood",
            "tempo": "strSpeed",
        }
        desired_tags_aliases = desired_tags_dict.keys()
        image_tags = [
            "strAlbumThumb",
            "strAlbumBack",
            "strAlbumCDart",
            "strAlbumSpine",
            "strAlbum3DCase",
            "strAlbum3DFlat",
            "strAlbum3DFace",
            "strAlbum3DThumb"
        ]

        response = helpers.request_helper(
            f"{self.BASE_URL}/searchalbum.php",
            {
                "s": artist,
                "a": album
            },
            ""
        )

        json_response = helpers.safe_json(response)["album"][0]
        print(json_response)

        with open(f"{self.ARTIST_METADATA_DIRECTORY}/{artist}.json", "r") as file:
            artist_metadata = json.load(file)

        found_album = False

        for album_index, album_item in enumerate(artist_metadata["releases"]["albums"]):

            if album.lower() == album_item["title"].lower():

                found_album = True

                for tag_alias in desired_tags_aliases:
                    if desired_tags_dict[tag_alias] in image_tags:
                        if not json_response.get(desired_tags_dict[tag_alias], None) is None and not json_response.get(desired_tags_dict[tag_alias], None) == "":
                            artist_metadata["releases"]["albums"][album_index]["media"][tag_alias] = json_response.get(desired_tags_dict[tag_alias], "N/A")
                    else:
                        if not json_response.get(desired_tags_dict[tag_alias], None) is None and not json_response.get(desired_tags_dict[tag_alias], None) == "":
                            artist_metadata["releases"]["albums"][album_index][tag_alias] = json_response.get(desired_tags_dict[tag_alias], "N/A")

        if not found_album:
            print(f"ERROR - Album not found in {self.ARTIST_METADATA_DIRECTORY}/{artist}.json")

        with open(f"{self.ARTIST_METADATA_DIRECTORY}/{artist}.json", "w") as file:
            json.dump(artist_metadata, file, indent=4)


"""
testClient = AudioDbClient()
testClient.search_artist("Rauw Alejandro")
testClient.search_album("Rauw Alejandro", "Cosa Nuestra")
"""
#response = helpers.request_helper("https://www.theaudiodb.com/api/v1/json/123/searchtrack.php", {"s": "Bad Bunny", "t": "El Club"}, "")
#print(response.json())
