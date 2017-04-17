import sys

import pytest
from moviepy.video.fx.blink import blink
from moviepy.video.VideoClip import TextClip
from test_helper import TMP_DIR, TRAVIS

sys.path.append("tests")

def test_duration():
    #TextClip returns the following error under Travis (issue with Imagemagick)
    #convert.im6: not authorized `@/tmp/tmpWL7I3M.txt' @ error/property.c/InterpretImageProperties/3057.
    #convert.im6: no images defined `PNG32:/tmp/tmpRZVqGQ.png' @ error/convert.c/ConvertImageCommand/3044.
    if TRAVIS:
       return
    
    clip = TextClip('hello world', size=(1280,720), color='white')
    clip.set_duration(5)
    assert clip.duration == 5

    clip2 = clip.fx(blink, d_on=1, d_off=1)
    clip2.set_duration(5)
    assert clip2.duration == 5

# Moved from tests.py. Maybe we can remove these?
def test_if_textclip_crashes_in_caption_mode():
    if TRAVIS:
       return
    
    TextClip(txt='foo', color='white', size=(640, 480), method='caption',
             align='center', fontsize=25)

def test_if_textclip_crashes_in_label_mode():
    if TRAVIS:
       return
    
    TextClip(txt='foo', method='label')

if __name__ == '__main__':
   pytest.main()
