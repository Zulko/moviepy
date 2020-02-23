import sys

import pytest

from moviepy.utils import close_all_clips
from moviepy.video.fx.blink import blink
from moviepy.video.VideoClip import TextClip

from .test_helper import FONT


def test_fontlist():
    TextClip.list('font')


def test_duration():
    clip = TextClip('hello world', size=(1280,720), color='white', font=FONT)
    clip = clip.set_duration(5)
    assert clip.duration == 5
    clip.close()

    clip2 = clip.fx(blink, d_on=1, d_off=1)
    clip2 = clip2.set_duration(5)
    assert clip2.duration == 5
    close_all_clips(locals())


# Moved from tests.py. Maybe we can remove these?
def test_if_textclip_crashes_in_caption_mode():
    TextClip(txt='foo', color='white', size=(640, 480), method='caption',
             align='center', fontsize=25, font=FONT).close()


def test_if_textclip_crashes_in_label_mode():
    TextClip(txt='foo', method='label', font=FONT).close()


if __name__ == '__main__':
    pytest.main()
