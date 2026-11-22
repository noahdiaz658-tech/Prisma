from mutagen.easyid3 import EasyID3
from pathlib import Path
import json, os, re
from libraryBuilder import LibraryBuilder

SONGS_DIRECTORY = r"../cache/media/songs"
LIBRARY_FILE = r"../cache/temp/Temp_Library.json"

def sanitize_filename(name:str):
    return re.sub(r'[<>:"/\\|?*]', "_", name)

class MetadataExtractor:

    def __init__(self):

        self.song_metadata = {
            "file-type" : "",
            "album" : "",
            "title": "",
            "artist": "",
            "tracknumber": "",
            "date": ""
        }

    def get_metadata(self, song_path:str):

        song_path = Path(song_path)

        if song_path.suffix == ".mp3":
            self.song_metadata["file-type"] = "mp3"
        elif song_path.suffix == ".flac":
            self.song_metadata["file-type"] = "flac"
        else:
            print("ERROR Not mp3.")

        if self.song_metadata["file-type"] == "mp3":

            keys = [key for key in self.song_metadata]
            song_audio = EasyID3(song_path)

            for index, key in enumerate(song_audio.keys(), start = 1):
                if key == keys[index]:
                    self.song_metadata[key] = song_audio.get(key, f"Couldn't find {key[0]}")[0]



        with open(rf"../cache/temp/song_metadata/{sanitize_filename(self.song_metadata['title'])}_Metadata.json", "w") as file:
            json.dump(self.song_metadata, file, indent = 4)

    def get_library_metadata(self, library_path:str):
        LBuilder = LibraryBuilder(SONGS_DIRECTORY)
        LBuilder.build_library()

        with open(library_path, "r") as file:
            library = json.load(file)

        for song in library:
            self.get_metadata(song)


extractor = MetadataExtractor()
extractor.get_library_metadata(LIBRARY_FILE)

#  'album', 'title', 'artist', 'tracknumber', 'date'
"""
print("Checksums: ")
print(f"Album: {song_audio.get("album", "No album detected")[0]}")
print(f"Title: {song_audio.get("title", "No title detected")[0]}")
print(f"Artist: {song_audio.get("artist", "No artist detected")[0]}")
print(f"Tracknumber: {song_audio.get("tracknumber", "No tracknumber detected")[0]}")
print(f"Date: {song_audio.get("date", "No date detected")[0]}")
"""