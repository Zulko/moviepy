# -*- coding: utf-8 -*-
"""Video file clip tests meant to be run with pytest."""
import os

from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.tools.credits import credits1
from moviepy.video.tools.cuts import detect_scenes
from moviepy.video.VideoClip import ColorClip

from tests.test_helper import FONT, TMP_DIR


def test_credits():
    credit_file = (
        "# This is a comment\n"
        "# The next line says : leave 4 blank lines\n"
        ".blank 2\n"
        "\n"
        "..Executive Story Editor\n"
        "MARCEL DURAND\n"
        "\n"
        ".blank 2\n"
        "\n"
        "..Associate Producers\n"
        "MARTIN MARCEL\n"
        "DIDIER MARTIN\n"
        "\n"
        "..Music Supervisor\n"
        "JEAN DIDIER\n"
    )

    file_location = os.path.join(TMP_DIR, "credits.txt")
    vid_location = os.path.join(TMP_DIR, "credits.mp4")
    with open(file_location, "w") as file:
        file.write(credit_file)

    image = credits1(
        file_location, 600, gap=100, stroke_color="blue", stroke_width=5, font=FONT
    )
    image = image.set_duration(3)
    image.write_videofile(vid_location, fps=24)
    assert os.path.isfile(vid_location)


def test_detect_scenes():
    """
    Test that a cut is detected between concatenated red and green clips
    """
    red = ColorClip((640, 480), color=(255, 0, 0)).set_duration(1)
    green = ColorClip((640, 480), color=(0, 200, 0)).set_duration(1)
    video = concatenate_videoclips([red, green])

    cuts, luminosities = detect_scenes(video, fps=10, logger=None)

    assert len(cuts) == 2
