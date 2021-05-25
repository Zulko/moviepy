"""Video file clip tests meant to be run with pytest."""

import math
import os

import pytest

from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.tools.credits import CreditsClip
from moviepy.video.tools.cuts import (
    FramesMatch,
    FramesMatches,
    detect_scenes,
    find_video_period,
)
from moviepy.video.VideoClip import BitmapClip, ColorClip

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

    image = CreditsClip(
        file_location, 600, gap=100, stroke_color="blue", stroke_width=5, font=FONT
    )
    image = image.with_duration(3)
    image.write_videofile(vid_location, fps=24, logger=None)
    assert image.mask
    assert os.path.isfile(vid_location)


def test_detect_scenes():
    """Test that a cut is detected between concatenated red and green clips."""
    red = ColorClip((640, 480), color=(255, 0, 0)).with_duration(1)
    green = ColorClip((640, 480), color=(0, 200, 0)).with_duration(1)
    video = concatenate_videoclips([red, green])

    cuts, luminosities = detect_scenes(video, fps=10, logger=None)

    assert len(cuts) == 2


def test_find_video_period():
    clip = VideoFileClip("media/chaplin.mp4").subclip(0, 0.5).loop(2)  # fps=25

    # you need to increase the fps to get correct results
    assert round(find_video_period(clip, fps=70), 6) == 0.5


@pytest.mark.parametrize(
    ("bitmap", "distance_threshold", "max_duration", "expected_matches"),
    (
        pytest.param(
            [
                ["RRR", "GGG", "BBB"],
                ["WWW", "WWW", "WWW"],
                ["WWW", "WWW", "WWW"],
                ["WWW", "WWW", "WWW"],
                ["RRR", "GGG", "BBB"],
                ["RRR", "GGG", "BBB"],
                ["WWW", "WWW", "WWW"],
                ["RRR", "GGG", "BBB"],
                ["WWW", "WWW", "WWW"],
            ],
            1,
            math.inf,
            [
                (1, 2, 0, 0),
                (1, 3, 0, 0),
                (2, 3, 0, 0),
                (0, 4, 0, 0),
                (0, 5, 0, 0),
                (4, 5, 0, 0),
                (1, 6, 0, 0),
                (2, 6, 0, 0),
                (3, 6, 0, 0),
                (0, 7, 0, 0),
                (4, 7, 0, 0),
                (5, 7, 0, 0),
                (1, 8, 0, 0),
                (2, 8, 0, 0),
                (3, 8, 0, 0),
                (6, 8, 0, 0),
            ],
            id="distance_threshold=1-max_duration=math.inf",
        ),
        pytest.param(
            [
                ["RRR", "GGG", "BBB"],
                ["WWW", "WWW", "WWW"],
                ["WWW", "WWW", "WWW"],
                ["WWW", "WWW", "WWW"],
                ["RRR", "GGG", "BBB"],
                ["RRR", "GGG", "BBB"],
                ["WWW", "WWW", "WWW"],
                ["RRR", "GGG", "BBB"],
                ["WWW", "WWW", "WWW"],
            ],
            1,
            2,
            [
                (1, 2, 0, 0),
                (1, 3, 0, 0),
                (2, 3, 0, 0),
                (4, 5, 0, 0),
                (5, 7, 0, 0),
                (6, 8, 0, 0),
            ],
            id="distance_threshold=1-max_duration=2",
        ),
        pytest.param(
            [
                ["RRR", "GGG", "BBB"],
                ["RRR", "GGG", "BBR"],
                ["RRR", "GGG", "BBB"],
                ["RRR", "GGG", "BRR"],
            ],
            70,
            2,
            [
                (0, 2, 0, 0),
                (0, 1, 69.4022, 69.4022),
                (1, 2, 69.4022, 69.4022),
                (1, 3, 69.4022, 69.4022),
            ],
            id="distance_threshold=70-max_duration=2",
        ),
    ),
)
def test_FramesMatches_from_clip(
    bitmap,
    expected_matches,
    distance_threshold,
    max_duration,
):
    clip = BitmapClip(bitmap, fps=1)

    matching_frames = FramesMatches.from_clip(
        clip,
        distance_threshold,
        max_duration,
        logger=None,
    )

    assert matching_frames
    assert isinstance(matching_frames, FramesMatches)
    assert isinstance(matching_frames[0], FramesMatch)

    for i, match in enumerate(matching_frames):
        for j, n in enumerate(match):
            assert round(n, 4) == expected_matches[i][j]


def test_FramesMatches_filter():
    input_matching_frames = [
        FramesMatch(1, 2, 0, 0),
        FramesMatch(1, 2, 0.8, 0.8),
        FramesMatch(1, 2, 0.8, 0),
    ]
    expected_matching_frames = [FramesMatch(1, 2, 0, 0)]
    matching_frames_filter = lambda x: not x.min_distance and not x.max_distance

    matching_frames = FramesMatches(input_matching_frames).filter(
        matching_frames_filter
    )

    assert len(matching_frames) == len(expected_matching_frames)
    for i, frames_match in enumerate(matching_frames):
        assert frames_match == expected_matching_frames[i]


def test_FramesMatches_save_load():
    input_matching_frames = [
        FramesMatch(1, 2, 0, 0),
        FramesMatch(1, 2, 0.8, 0),
        FramesMatch(1, 2, 0.8, 0.8),
    ]
    expected_frames_matches_file_content = """1.000	2.000	0.000	0.000
1.000	2.000	0.800	0.000
1.000	2.000	0.800	0.800
"""

    outputfile = os.path.join(TMP_DIR, "moviepy_FramesMatches_save_load.txt")

    # save
    FramesMatches(input_matching_frames).save(outputfile)

    with open(outputfile, "r") as f:
        assert f.read() == expected_frames_matches_file_content

    # load
    for i, frames_match in enumerate(FramesMatches.load(outputfile)):
        assert frames_match == input_matching_frames[i]


if __name__ == "__main__":
    test_credits()
