"""
Tests meant to be run with pytest
"""

import sys
import os
import pytest

from moviepy.editor import *


#@pytest.fixture
#def example_video1():
#    pass

global knights, knights10

def download_youtube_video(url, filename):
    if not os.path.exists(filename):
       print("\nDownloading %s\n" % filename)
       download_webfile(url, filename)
       print("Downloading complete...\n")


def test_download_media(capsys):
    global knights, knights10

    with capsys.disabled():
       download_youtube_video("zvCvOC2VwDc", "media/knights.mp4")

    knights=VideoFileClip("media/knights.mp4")
    knights10 = knights.subclip(60,70)


def test_issue_145():
    with pytest.raises(Exception, message="Expecting Exception"):
         _final = concatenation([knights10], method = 'composite')

def test_issue_407():
    assert round(knights.fps) == 30
    assert knights10.fps == knights.fps

    _text=TextClip("blah").set_duration(2)  #TextClip has no fps attribute

    _video=concatenate_videoclips([_text, knights10, knights10])
    assert _video.fps == knights10.fps

    # uncomment when PR 416 is merged.
    #_video=concatenate_videoclips([_text])
    #assert _video.fps == None


def test_PR_306():
    assert TextClip.list('font') != []
    assert TextClip.list('color') != []

    with pytest.raises(Exception, message="Expecting Exception"):
         TextClip.list('blah')

if __name__ == '__main__':
   pytest.main()
