"""
Tests meant to be run with pytest
"""

import os
import pytest

from moviepy.editor import *

def download_url(url, filename):
    if not os.path.exists(filename):
       print("\nDownloading %s\n" % filename)
       download_webfile(url, filename)
       print("Downloading complete...\n")

def download_youtube_video(youtube_id, filename):
    # FYI..  travis-ci doesn't like youtube-dl
    download_url(youtube_id, filename)

def test_download_media(capsys):
    with capsys.disabled():
       #download_youtube_video("zvCvOC2VwDc", "media/knights.mp4")
       download_url("https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/Python_logo_and_wordmark.svg/260px-Python_logo_and_wordmark.svg.png",
                    "media/python_logo.png")

    #knights=VideoFileClip("media/knights.mp4")
    #knights10 = knights.subclip(60,70)


def test_issue_145():
    _video = ColorClip((800, 600), col=(255,0,0)).set_duration(5)
    with pytest.raises(Exception, message="Expecting Exception"):
         _final = concatenation([_video], method = 'composite')
        
def test_issue_285():
    clip_1 = ImageClip('media/python_logo.png', duration=10)
    clip_2 = ImageClip('media/python_logo.png', duration=10)
    clip_3 = ImageClip('media/python_logo.png', duration=10)

    merged_clip = concatenate_videoclips([clip_1, clip_2, clip_3])

    def test_issue_407():
    assert round(knights.fps) == 30
    assert knights10.fps == knights.fps

def test_issue_407():
    _red = ColorClip((800, 600), col=(255,0,0)).set_duration(5)
    _red.fps=30
    assert round(_red.fps) == 30

    _green=ColorClip((640, 480), col=(0,255,0)).set_duration(2)  #ColorClip has no fps attribute
    _blue=ColorClip((640, 480), col=(0,0,255)).set_duration(2)  #ColorClip has no fps attribute

    _video=concatenate_videoclips([_red, _green, _blue])
    assert _video.fps == _red.fps

    # uncomment when PR 416 is merged.
    #_video1=concatenate_videoclips([_green])
    #assert _video1.fps == None

def test_issue_417():
    # failed in python2

    cad = u'media/python_logo.png'
    myclip = ImageClip(cad).fx(vfx.resize, newsize=[1280, 660])
    final = CompositeVideoClip([myclip], size=(1280, 720))
    #final.set_duration(7).write_videofile("test.mp4", fps=30)

if __name__ == '__main__':
   pytest.main()