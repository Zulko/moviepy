# -*- coding: utf-8 -*-
from moviepy.video.io.ffmpeg_reader import ffmpeg_parse_infos
import pytest

media = "D://1.mp4"


def test_one():
    infos = ffmpeg_parse_infos(media)
    assert infos["audio_bitrate"]
    assert infos["video_bitrate"]


if __name__ == "__main__":
    pytest.main()
