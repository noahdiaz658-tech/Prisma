import time

from backend.APIs import LrcLibAPI, MusicBrainzAPI, LastFmAPI, DeezerAPI, AudioDbAPI, WikipediaAPI
from backend.APIs.AudioDbAPI import AudioDbClient

LyricsClient = LrcLibAPI.LrcLibClient()
MusicBrainzClient = MusicBrainzAPI.MusicBrainzClient()
LastFMClient = LastFmAPI.LastFmClient()
DeezerClient = DeezerAPI.DeezerClient()
AudioDbClient = AudioDbAPI.AudioDbClient()
WikipediaClient = WikipediaAPI.WikipediaClient()

#Artist_MBID = MBClient.get_MBIB("Radiohead")
#MBClient.get_artist_albums("Radiohead", MBClient.get_MBIB("Radiohead"))
#FMClient.search_albums("Radiohead", "OK Computer")
#FMClient.add_top_album_tags("Radiohead", "OK Computer", "artist")
#FMClient.get_similar_artists("Cris MJ")
#FMClient.get_top_artists_chart()


current_aritst = "JHAYCO"
MusicBrainzClient.search_artist(current_aritst)
time.sleep(3)
Artist_MBID = MusicBrainzClient.get_MBIB(current_aritst)
LastFMClient.get_similar_artists(current_aritst)
DeezerClient.search_artist(current_aritst)
time.sleep(3)
DeezerClient.get_artist_albums(current_aritst)
AudioDbClient.search_artist(current_aritst)
WikipediaClient.search_artist(current_aritst)
DeezerClient.resolve_genres()

