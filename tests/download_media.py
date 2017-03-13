import os

from moviepy.editor import *

def download_url(url, filename):
    if not os.path.exists(filename):
       print("\nDownloading %s\n" % filename)
       download_webfile(url, filename)
       print("Downloading complete...\n")

def download_youtube_video(youtube_id, filename):
    # FYI..  travis-ci doesn't like youtube-dl
    download_url(youtube_id, filename)


def download():
    if not os.path.exists("media"):
       os.mkdir("media")

    download_url("https://github.com/earney/moviepy_media/raw/master/tests/images/python_logo.png",
                 "media/python_logo.png")

    download_url("https://github.com/earney/moviepy_media/raw/master/tests/images/matplotlib_demo1.png",
                 "media/matplotlib_demo1.png")

    download_url("https://github.com/earney/moviepy_media/raw/master/tests/images/afterimage.png",
                 "media/afterimage.png")

    download_url("https://github.com/earney/moviepy_media/raw/master/tests/videos/big_buck_bunny_432_433.webm",
                 "media/big_buck_bunny_432_433.webm")

    download_url("https://github.com/earney/moviepy_media/raw/master/tests/sounds/crunching.mp3",
                 "media/crunching.mp3")
