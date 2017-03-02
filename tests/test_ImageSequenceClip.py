import pytest
from moviepy.editor import *

# must have to work on travis-ci
import sys
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
        images.append("media/matplotlib_demo1.png")

    clip=ImageSequenceClip(images, durations=durations)
    assert clip.duration == sum(durations)
    clip.write_videofile("/tmp/ImageSequenceClip1.mp4", fps=30)

if __name__ == '__main__':
   pytest.main()
