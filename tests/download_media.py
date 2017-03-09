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

    download_url("https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/Python_logo_and_wordmark.svg/260px-Python_logo_and_wordmark.svg.png",
                 "media/python_logo.png")

    download_url("http://matplotlib.org/_images/barh_demo.png",
                 "media/matplotlib_demo1.png")

    download_url("https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Afterimagenpov.svg/1200px-Afterimagenpov.svg.png",
                 "media/afterimage.png")

    download_url("http://www.4uall.net/free-sound-effects/Animal-Music-free-sound-effects/COW_BIRD.WAV",
                 "media/cow_bird.wav")

    download_url("https://www.soundjay.com/ambient/boarding-accouncement-1.mp3",
                 "media/boarding_announcement.mp3")

    download_url("https://www.soundjay.com/human/crunching-1.mp3",
                 "media/crunching.mp3")
