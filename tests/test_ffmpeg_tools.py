import os

from moviepy.video.io.ffmpeg_tools import ffmpeg_stabilize_video
from tests.test_helper import TMP_DIR


def test_stabilize_video():
    ffmpeg_stabilize_video("media/fire2.mp4", output_dir=TMP_DIR, overwrite_file=True)
    assert os.path.exists(os.path.join(TMP_DIR, "fire2_stabilized.mp4"))
