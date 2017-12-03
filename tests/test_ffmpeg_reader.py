# -*- coding: utf-8 -*-
"""FFmpeg reader tests meant to be run with pytest."""
import sys

import pytest
from moviepy.video.io.ffmpeg_reader import ffmpeg_parse_infos, FFMPEG_VideoReader

sys.path.append("tests")

import download_media


def test_download_media(capsys):
    with capsys.disabled():
       download_media.download()

def test_ffmpeg_parse_infos():
    d=ffmpeg_parse_infos("media/big_buck_bunny_432_433.webm")
    assert d['duration'] == 1.0

    d=ffmpeg_parse_infos("media/pigs_in_a_polka.gif")
    assert d['video_size'] == [314, 273]
    assert d['duration'] == 3.0

def test_autorotate():
    # This test requires ffmpeg >=2.7
    video_file = 'media/ficus_vertical.mp4'
    reader = FFMPEG_VideoReader(video_file)
    assert reader.infos['video_size'] == [1920, 1080]
    assert reader.infos['video_rotation'] == 90
    assert reader.size == [1080, 1920]
    reader.close()

    reader = FFMPEG_VideoReader(video_file, ffmpeg_params=['-noautorotate'])
    assert reader.size == [1920, 1080]
    assert reader.rotation == 90
    reader.close()


if __name__ == '__main__':
   pytest.main()
