# -*- coding: utf-8 -*-
"""FFmpeg reader tests meant to be run with pytest."""
import sys

import pytest
from moviepy.video.io.ffmpeg_reader import ffmpeg_parse_infos

from . import download_media

sys.path.append("tests")


def test_download_media(capsys):
    with capsys.disabled():
       download_media.download()

def test_ffmpeg_parse_infos():
    d=ffmpeg_parse_infos("media/big_buck_bunny_432_433.webm")
    assert d['duration'] == 1.0

    d=ffmpeg_parse_infos("media/pigs_in_a_polka.gif")
    assert d['video_size'] == [314, 273]
    assert d['duration'] == 3.0
    assert not d['audio_found']

    d=ffmpeg_parse_infos("media/video_with_failing_audio.mp4")
    assert d['audio_found']
    assert d['audio_fps'] == 44100

    d=ffmpeg_parse_infos("media/crunching.mp3")
    assert d['audio_found']
    assert d['audio_fps'] == 48000


if __name__ == '__main__':
   pytest.main()
