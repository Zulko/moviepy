"""Tset for moviepy utils."""
import os
import threading
from time import sleep

import pytest

from moviepy import VideoFileClip
from moviepy.utils import stop_processing_video


@pytest.mark.parametrize("output_path", ["test_stop.mp4", "examples/test_stop.mp4"])
def test_stop_processing_video(output_path):
    """Make sure "stop_processing_video" works by checking the output file."""
    t1 = threading.Thread(
        target=lambda: VideoFileClip(
            "media/sintel_with_14_chapters.mp4"
        ).write_videofile(output_path)
    )

    t1.start()
    sleep(1)
    stop_processing_video(output_path)
    assert os.path.isfile(output_path) is False
