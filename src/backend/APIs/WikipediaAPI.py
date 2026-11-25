import wikipediaapi
import json
from pathlib import Path
import src.backend.helpers as helpers

class WikipediaClient:

    def __init__(self):
        self.ARTIST_METADATA_DIRECTORY = "../cache/temp/artist_metadata"
        self.wiki = wikipediaapi.Wikipedia(
            user_agent=f"PrismaMusic/v0.1 ({helpers.EMAIL_ADDRESS})",
            language="en"
        )

    def search_artist(self, artist):

        if Path(f"{self.ARTIST_METADATA_DIRECTORY}/{artist}.json").exists():
            with open(f"{self.ARTIST_METADATA_DIRECTORY}/{artist}.json", "r") as file:
                artist_metadata = json.load(file)

            if artist_metadata["no-audiodb-metadata"]:
                page = self.wiki.page(artist)
                artist_metadata["bio"] = page.summary

                with open(f"{self.ARTIST_METADATA_DIRECTORY}/{artist}.json", "w") as file:
                    json.dump(artist_metadata, file, indent=4)




"""
test_client = WikipediaClient()
test_client.search_artist("Cris MJ")
"""
