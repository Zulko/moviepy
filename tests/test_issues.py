"""
Tests meant to be run with pytest
"""

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
        
def test_issue_417():
    # failed in python2

    cad = u'media/python_logo.png'
    myclip = ImageClip(cad).fx(vfx.resize, newsize=[1280, 660])
    final = CompositeVideoClip([myclip], size=(1280, 720))
    #final.set_duration(7).write_videofile("test.mp4", fps=30)

def test_issue_407():
    assert round(knights.fps) == 30
    assert knights10.fps == knights.fps

    _text=TextClip("blah").set_duration(2)  #TextClip has no fps attribute

    _video=concatenate_videoclips([_text, knights10, knights10])
    assert _video.fps == knights10.fps

    # uncomment when PR 416 is merged.
    #_video=concatenate_videoclips([_text])
    #assert _video.fps == None


def test_issue_417():
    # failed in python2

    cad = u'media/python_logo.png'
    myclip = ImageClip(cad).fx(vfx.resize, newsize=[1280, 660])
    final = CompositeVideoClip([myclip], size=(1280, 720))
    #final.set_duration(7).write_videofile("test.mp4", fps=30)

if __name__ == '__main__':
   pytest.main()
