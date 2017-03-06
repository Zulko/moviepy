"""
Tests meant to be run with pytest
"""

import sys
import os
import pytest

from moviepy.editor import *


def test_PR_306():
    #put this back in once we get ImageMagick working on travis-ci
    #assert TextClip.list('font') != []
    #assert TextClip.list('color') != []

    #with pytest.raises(Exception, message="Expecting Exception"):
    #     TextClip.list('blah')
    pass


def test_PR_339():
    #in caption mode
    #overlay = TextClip(txt='foo',
    #                   color='white',
    #                   size=(640, 480),
    #                   method='caption',
    #                   align='center',
    #                   fontsize=25)

    #in_label_mode
    #overlay = TextClip(txt='foo', method='label')
    pass


def test_PR_424():
    # Recommended use
    clip = ColorClip([1000, 600], color=(60, 60, 60), duration=10)
    # Uses `col` so should work the same as above, but give warning
    clip = ColorClip([1000, 600], col=(60, 60, 60), duration=10)
    # Should give 2 warnings and use `color`, not `col`
    clip = ColorClip([1000, 600], color=(60, 60, 60), duration=10, col=(2,2,2))


def test_PR_458():
    clip = ColorClip([1000, 600], color=(60, 60, 60), duration=10)
    clip.write_videofile("test.mp4", progress_bar=False, fps=30)

if __name__ == '__main__':
   pytest.main()
