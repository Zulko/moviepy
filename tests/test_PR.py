"""
Tests meant to be run with pytest
"""

import sys
import os
import pytest

from moviepy.editor import *

from moviepy.video.tools.interpolators import Trajectory

import sys
sys.path.append("tests")
import download_media
from test_helper import PYTHON_VERSION, TMP_DIR, TRAVIS

def test_download_media(capsys):
    with capsys.disabled():
       download_media.download()

def test_PR_306():
    if TRAVIS:
       return

    #put this back in once we get ImageMagick working on travis-ci
    assert TextClip.list('font') != []
    assert TextClip.list('color') != []

    with pytest.raises(Exception, message="Expecting Exception"):
         TextClip.list('blah')


def test_PR_339():
    if TRAVIS:
       return

    #in caption mode
    overlay = TextClip(txt='foo',
                       color='white', font="Liberation-Mono",
                       size=(640, 480),
                       method='caption',
                       align='center',
                       fontsize=25)

    #in_label_mode
    overlay = TextClip(txt='foo', font="Liberation-Mono", method='label')


def test_PR_373():
    result = Trajectory.load_list("media/traj.txt")

    Trajectory.save_list(result, os.path.join(TMP_DIR, "traj1.txt"))

    result1 = Trajectory.load_list(os.path.join(TMP_DIR,"traj1.txt"))

    assert len(result[0].tt) == len(result1[0].tt)
    for i in range(len(result[0].tt)):
        assert result[0].tt[i] == result1[0].tt[i]

    assert len(result[0].xx) == len(result1[0].xx)
    for i in range(len(result[0].xx)):
        assert result[0].xx[i] == result1[0].xx[i]

    assert len(result[0].yy) == len(result1[0].yy)
    for i in range(len(result[0].yy)):
        assert result[0].yy[i] == result1[0].yy[i]


def test_PR_424():
    # Recommended use
    clip = ColorClip([1000, 600], color=(60, 60, 60), duration=10)
    # Uses `col` so should work the same as above, but give warning
    clip = ColorClip([1000, 600], col=(60, 60, 60), duration=10)
    # Should give 2 warnings and use `color`, not `col`
    clip = ColorClip([1000, 600], color=(60, 60, 60), duration=10, col=(2,2,2))


def test_PR_458():
    clip = ColorClip([1000, 600], color=(60, 60, 60), duration=10)
    clip.write_videofile(os.path.join(TMP_DIR, "test.mp4"),
                         progress_bar=False, fps=30)


def test_PR_515():
    # Won't actually work until video is in download_media
    clip = VideoFileClip("media/fire2.mp4", fps_source='tbr')
    assert clip.fps == 90000
    clip = VideoFileClip("media/fire2.mp4", fps_source='fps')
    assert clip.fps == 10.51

def test_PR_529():
    video_clip = VideoFileClip("media/fire2.mp4")
    assert video_clip.rotation ==180

if __name__ == '__main__':
   pytest.main()
