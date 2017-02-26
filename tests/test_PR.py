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

if __name__ == '__main__':
   pytest.main()
