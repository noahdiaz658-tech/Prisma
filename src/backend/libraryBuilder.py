import os, json
from pathlib import Path

LIBRARY_FILE = r"../cache/temp/Temp_Library.json"

class LibraryBuilder:

    def __init__(self, media_directory):

        self.media_directory = Path(media_directory).resolve()
        self.library = []


    def build_library(self):

        for root, dirs, files, in os.walk(self.media_directory, topdown= True):
            for file in files:
                if file.endswith(".mp3") | file.endswith(".flac"):
                    self.library.append(os.path.join(root, file))

        with open(LIBRARY_FILE, "w") as library_file:
            json.dump(self.library, library_file, indent=4)

    def get_library(self):
        return self.library


