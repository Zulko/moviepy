# -*- coding: utf-8 -*-
"""Pull request tests meant to be run with pytest."""
import os
import sys

import pytest
from moviepy.video.fx.scroll import scroll
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.tools.interpolators import Trajectory
from moviepy.video.VideoClip import ColorClip, ImageClip, TextClip

sys.path.append("tests")
from test_helper import TMP_DIR, TRAVIS

def test_download_media(capsys):
    """Test downloading."""
    import download_media
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

    # In caption mode.
    TextClip(txt='foo', color='white', font="Liberation-Mono", size=(640, 480),
             method='caption', align='center', fontsize=25)

    # In label mode.
    TextClip(txt='foo', font="Liberation-Mono", method='label')

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
    """Ensure deprecation and user warnings are triggered."""
    import warnings
    warnings.simplefilter('always') # Alert us of deprecation warnings.

    # Recommended use
    ColorClip([1000, 600], color=(60, 60, 60), duration=10)

    with pytest.warns(DeprecationWarning):
        # Uses `col` so should work the same as above, but give warning.
        ColorClip([1000, 600], col=(60, 60, 60), duration=10)

    # Catch all warnings as record.
    with pytest.warns(None) as record:
        # Should give 2 warnings and use `color`, not `col`
        ColorClip([1000, 600], color=(60, 60, 60), duration=10, col=(2,2,2))

    message1 = 'The `ColorClip` parameter `col` has been deprecated. ' + \
               'Please use `color` instead.'
    message2 = 'The arguments `color` and `col` have both been passed to ' + \
               '`ColorClip` so `col` has been ignored.'

    # Assert that two warnings popped and validate the message text.
    assert len(record) == 2
    assert str(record[0].message) == message1
    assert str(record[1].message) == message2

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


def test_PR_528():
    clip = ImageClip("media/vacation_2017.jpg")
    new_clip = scroll(clip, w=1000, x_speed=50)
    new_clip = new_clip.set_duration(20)
    new_clip.fps = 24
    new_clip.write_videofile(os.path.join(TMP_DIR, "pano.mp4"))


def test_PR_529():
    video_clip = VideoFileClip("media/fire2.mp4")
    assert video_clip.rotation == 180


if __name__ == '__main__':
   pytest.main()
