"""
Tests meant to be run with pytest
"""
import sys
sys.path.append("../moviepy")

import pytest
from tempfile import NamedTemporaryFile

from moviepy.editor import *


@pytest.fixture
def example_video1():
    pass

def test_all():

    test_clips = []

    # test video make from color or image
    color_clip = ColorClip(size=(360, 240), duration=10.0)
    test_clips.append(color_clip)

    image = "./tests/media/logo.png"
    image_clip = ImageClip(image, duration=10.0)
    test_clips.append(image_clip)

    for clip in test_clips:
        with NamedTemporaryFile(suffix=".mp4") as temp_file:
            clip.set_audio(AudioClip(lambda t: 0.0, duration=clip.duration))
            clip.write_videofile(temp_file.name, fps=24)
            test_video_clip = VideoFileClip(temp_file.name)
            with NamedTemporaryFile(suffix=".mp4") as new_temp_file:
                test_video_clip.write_videofile(new_temp_file.name, fps=24)

    # test video with short duration
    video = "./tests/media/test_video.mp4"
    video_clip = VideoFileClip(video)
    video_clip.set_duration(1.0)
    with NamedTemporaryFile(suffix=".mp4") as temp_file:
        video_clip.write_videofile(temp_file.name, fps=24)
        test_video_clip = VideoFileClip(temp_file.name)
        with NamedTemporaryFile(suffix=".mp4") as new_temp_file:
            test_video_clip.write_videofile(new_temp_file.name, fps=24)

    
