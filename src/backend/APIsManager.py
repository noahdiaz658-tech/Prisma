import time

from backend.APIs import LrcLibAPI, MusicBrainzAPI, LastFmAPI, DeezerAPI

LyricsClient = LrcLibAPI.LrcLibClient()
MusicBrainzClient = MusicBrainzAPI.MusicBrainzClient()
LastFMClient = LastFmAPI.LastFmClient()
DeezerClient = DeezerAPI.DeezerClient()

#Artist_MBID = MBClient.get_MBIB("Radiohead")
#MBClient.get_artist_albums("Radiohead", MBClient.get_MBIB("Radiohead"))
#FMClient.search_albums("Radiohead", "OK Computer")
#FMClient.add_top_album_tags("Radiohead", "OK Computer", "artist")
#FMClient.get_similar_artists("Cris MJ")
#FMClient.get_top_artists_chart()

Artist_MBID = MusicBrainzClient.get_MBIB("Rauw Alejandro")
LastFMClient.get_similar_artists("Rauw Alejandro")
DeezerClient.search_artist("Rauw Alejandro")
time.sleep(3)
DeezerClient.get_artist_albums("Rauw Alejandro")
time.sleep(3)


"""
DZClient.search_artist("Bad Bunny")
time.sleep(3)
DZClient.get_artist_albums("Bad Bunny")
time.sleep(3)
DZClient.get_similar_artists("Bad Bunny")
time.sleep(3)
#DZClient.get_top_songs("Bad Bunny")
"""



"""
image_response = requests.get("https://lastfm-img.freetls.fastly.net/i/u/34s/2a96cbd8b46e442fc41c2b86b821562f.png")
with open("test.png", "wb") as pic:
    pic.write(image_response.content)
"""