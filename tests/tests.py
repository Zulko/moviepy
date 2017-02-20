"""
Tests meant to be run with pytest
"""

import pytest

from moviepy.editor import *


@pytest.fixture
def example_video1():
    pass

_knights=VideoFileClip("media/knights.mp4")
_knights10 = _knights.subclip(60,70)

# issue 145
with pytest.raises(Exception, message="Expecting Exception"):
     _final = concatenation([_knights10], method = 'composite')
