# -*- coding: utf-8 -*-
"""Image sequencing clip tests meant to be run with pytest."""
import os
import sys

import pytest
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip

sys.path.append("tests")
import download_media
from test_helper import TMP_DIR

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
        images.append("media/python_logo_upside_down.png")

    clip = ImageSequenceClip(images, durations=durations)
    assert clip.duration == sum(durations)
    clip.write_videofile(os.path.join(TMP_DIR, "ImageSequenceClip1.mp4"), fps=30)

def test_black_white():  # issue 190
    from PIL import Image

    images=[]
    image1 = Image.open("media/python_logo.png")
    image1 = image1.convert('1')  #convert to black and white
    image1.save(os.path.join(TMP_DIR, "python_logo_bw1.png"))
    images.append(os.path.join(TMP_DIR, "python_logo_bw1.png"))

    image2 = Image.open("media/python_logo_upside_down.png")
    image2 = image2.convert('1')  #convert to black and white
    image2.save(os.path.join(TMP_DIR, "python_logo_bw2.png"))
    images.append(os.path.join(TMP_DIR, "python_logo_bw2.png"))

    clip = ImageSequenceClip(images, fps=1)
    clip.write_videofile(os.path.join(TMP_DIR, "issue_190.mp4"))

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
   test_black_white()
   #pytest.main()
