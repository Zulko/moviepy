# -*- coding: utf-8 -*-
from moviepy.video.io.ffmpeg_reader import ffmpeg_parse_infos
import pytest
import sys
sys.path.append("tests")


def test_one():
    infos = ffmpeg_parse_infos("tests/resource/1.mp4")
    assert infos["audio_bitrate"]
    assert infos["video_bitrate"]


if __name__ == "__main__":
    pytest.main()
