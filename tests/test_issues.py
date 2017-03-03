"""
Tests meant to be run with pytest
"""

import os
import pytest

from moviepy.editor import *

# must have to work on travis-ci
import sys
sys.path.append("tests")
import download_media

def test_download_media(capsys):
    with capsys.disabled():
       download_media.download()

def test_issue_145():
    video = ColorClip((800, 600), color=(255,0,0)).set_duration(5)
    with pytest.raises(Exception, message="Expecting Exception"):
         final = concatenate_videoclips([video], method = 'composite')

def test_issue_407():
    red = ColorClip((800, 600), color=(255,0,0)).set_duration(5)
    red.fps=30
    assert red.fps == 30
    assert red.w == 800
    assert red.h == 600
    assert red.size == (800, 600)

    #ColorClip has no fps attribute
    green=ColorClip((640, 480), color=(0,255,0)).set_duration(2)
    blue=ColorClip((640, 480), color=(0,0,255)).set_duration(2)

    assert green.w == blue.w == 640
    assert green.h == blue.h == 480
    assert green.size == blue.size == (640, 480)

    with pytest.raises(AttributeError, message="Expecting ValueError Exception"):
         green.fps

    with pytest.raises(AttributeError, message="Expecting ValueError Exception"):
         blue.fps

    video=concatenate_videoclips([red, green, blue])
    assert video.fps == red.fps

def test_issue_416():
    green=ColorClip((640, 480), color=(0,255,0)).set_duration(2)  #ColorClip has no fps attribute
    video1=concatenate_videoclips([green])
    assert video1.fps == None

def test_issue_417():
    # failed in python2

    cad = u'media/python_logo.png'
    myclip = ImageClip(cad).fx(vfx.resize, newsize=[1280, 660])
    final = CompositeVideoClip([myclip], size=(1280, 720))
    #final.set_duration(7).write_videofile("test.mp4", fps=30)

if __name__ == '__main__':
   pytest.main()
