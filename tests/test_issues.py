"""
Tests meant to be run with pytest
"""

import sys
import os
import pytest

from moviepy.editor import *


global knights, knights10

def download_url(url, filename):
    if not os.path.exists(filename):
       print("\nDownloading %s\n" % filename)
       download_webfile(url, filename)
       print("Downloading complete...\n")

def download_youtube_video(youtube_id, filename):
    download_url(youtube_id, filename)


def test_download_media(capsys):
    global knights, knights10
    
    with capsys.disabled():
       download_youtube_video("zvCvOC2VwDc", "media/knights.mp4")
       download_url("https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/Python_logo_and_wordmark.svg/260px-Python_logo_and_wordmark.svg.png",
                    "media/python_logo.png")

    knights=VideoFileClip("media/knights.mp4")
    knights10 = knights.subclip(60,70)



def test_issue_145():
    with pytest.raises(Exception, message="Expecting Exception"):
         _final = concatenation([knights10], method = 'composite')

def test_issue_285():
    clip_1 = ImageClip('media/python_logo.png', duration=10)
    clip_2 = ImageClip('media/python_logo.png', duration=10)
    clip_3 = ImageClip('media/python_logo.png', duration=10)

    merged_clip = concatenate_videoclips([clip_1, clip_2, clip_3])
