"""
To run the tests:
    py.test tests.py
"""

from moviepy.editor import *

#@pytest.fixture
def test_if_TextClip_crashes():
    overlay = TextClip(txt='foo',
                       color='white',
                       size=(640, 480),
                       method='caption',
                       align='center',
                       fontsize=25)
