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

def test_issue_285():
    clip_1 = ImageClip('media/python_logo.png', duration=10)
    clip_2 = ImageClip('media/python_logo.png', duration=10)
    clip_3 = ImageClip('media/python_logo.png', duration=10)

    merged_clip = concatenate_videoclips([clip_1, clip_2, clip_3])
    assert merged_clip.duration == 30

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

def test_issue_467():
    cad = 'media/python_logo.png'
    clip = ImageClip(cad)

    #caused an error, NameError: global name 'copy' is not defined
    clip = clip.fx(vfx.blink, d_on=1, d_off=1)

def test_issue_470():
    audio_clip = AudioFileClip('media/crunching.mp3')

    # t_end is out of bounds
    subclip = audio_clip.subclip(t_start=6, t_end=9)

    with pytest.raises(IOError, message="Expecting IOError"):
         subclip.write_audiofile('/tmp/issue_470.wav', write_logfile=True)


if __name__ == '__main__':
   pytest.main()
