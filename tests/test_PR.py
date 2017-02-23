"""
Tests meant to be run with pytest
"""

import sys
import os
import pytest

from moviepy.editor import *

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



def test_PR_306():
    assert TextClip.list('font') != []
    assert TextClip.list('color') != []

    with pytest.raises(Exception, message="Expecting Exception"):
         TextClip.list('blah')


def test_PR_339():
    #in caption mode
    overlay = TextClip(txt='foo',
                       color='white',
                       size=(640, 480),
                       method='caption',
                       align='center',
                       fontsize=25)

    #in_label_mode
    overlay = TextClip(txt='foo', method='label')

if __name__ == '__main__':
   pytest.main()
