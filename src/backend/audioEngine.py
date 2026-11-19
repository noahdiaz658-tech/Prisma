import os
from libraryBuilder import LibraryBuilder

os.environ["PATH"] = r"C:\Tools\mpv;" + os.environ["PATH"]

import mpv
from pathlib import Path

LIBRARY_FILE = r"../cache/temp/Temp_Library.json"
MEDIA_DIRECTORY = r"../cache/songs"

class AudioEngine:

    def __init__(self):

        self.player = mpv.MPV()
        self.player.volume = 50
        self.builder = LibraryBuilder(MEDIA_DIRECTORY)
        self.builder.build_library()

        self.library = self.builder.get_library()
        self.song_index = 0



    def play(self):
        self.player.play(self.library[self.song_index])

    def toggle_pause(self):
        self.player.pause()

    def skip(self):
        if self.song_index < len(self.library) - 1:
            self.song_index += 1
        else:
            self.song_index = 0

        self.play()


    def back(self):
        if self.song_index != 0:
            self.song_index -= 1
        else:
            self.song_index = len(self.library) - 1

        self.play()

    def change_volume(self, volume:int):
        self.player.volume = volume

    def seek(self, pos:int):
        self.player.seek(pos, reference="absolute")

    def seek_skip(self, seconds:int):
        self.player.seek(seconds)

    def stop(self):
        self.player.stop()

engine = AudioEngine()

while True:
    engine.play()

"""
    user_input = input("Type 's' to skip: ")
    if user_input == "skip":
        engine.skip()
    elif user_input == "b":
        engine.back()
"""