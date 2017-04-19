# -*- coding: utf-8 -*-
"""Image sequencing clip tests meant to be run with pytest."""
import sys

import pytest
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip

sys.path.append("tests")
import download_media

def test_download_media(capsys):
    with capsys.disabled():
       download_media.download()

def test_1():
    images=[]
    durations=[]

    for i in range(5):
        durations.append(i)
        images.append("media/python_logo.png")
        durations.append(i)
        images.append("media/python_logo.png")
        #images.append("media/matplotlib_demo1.png")

    clip = ImageSequenceClip(images, durations=durations)
    assert clip.duration == sum(durations)
    clip.write_videofile("/tmp/ImageSequenceClip1.mp4", fps=30)

def test_2():
    images=[]
    durations=[]

    durations.append(1)
    images.append("media/python_logo.png")
    durations.append(2)
    images.append("media/matplotlib_demo1.png")

    #images are not the same size..
    with pytest.raises(Exception, message='Expecting Exception'):
         ImageSequenceClip(images, durations=durations)


if __name__ == '__main__':
   pytest.main()
