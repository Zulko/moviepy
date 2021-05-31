"""Video file clip tests meant to be run with pytest."""

import importlib
import math
import os
import shutil
import sys

import numpy as np
import pytest

from moviepy.audio.AudioClip import AudioClip, CompositeAudioClip
from moviepy.audio.fx.multiply_volume import multiply_volume
from moviepy.audio.tools.cuts import find_audio_period
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.fx.loop import loop
from moviepy.video.fx.time_mirror import time_mirror
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.tools.credits import CreditsClip
from moviepy.video.tools.cuts import (
    FramesMatch,
    FramesMatches,
    detect_scenes,
    find_video_period,
)
from moviepy.video.tools.drawing import circle, color_gradient, color_split
from moviepy.video.VideoClip import BitmapClip, ColorClip, ImageClip, VideoClip

from tests.test_helper import FONT, TMP_DIR, get_mono_wave, get_stereo_wave


try:
    importlib.import_module("ipython.display")
except ImportError:
    ipython_available = False
else:
    ipython_available = True
    del sys.modules["ipython.display"]


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


@pytest.mark.parametrize(
    ("n", "percent", "expected_result"),
    (
        pytest.param(1, None, FramesMatch(1, 2, 0, 0), id="n=1"),
        pytest.param(
            2,
            None,
            FramesMatches([FramesMatch(1, 2, 0, 0), FramesMatch(2, 3, 0, 0)]),
            id="n=2",
        ),
        pytest.param(
            1,
            50,
            FramesMatches([FramesMatch(1, 2, 0, 0), FramesMatch(2, 3, 0, 0)]),
            id="percent=50",
        ),
    ),
)
def test_FramesMatches_best(n, percent, expected_result):
    assert (
        FramesMatches(
            [
                FramesMatch(1, 2, 0, 0),
                FramesMatch(2, 3, 0, 0),
                FramesMatch(4, 5, 0, 0),
                FramesMatch(5, 6, 0, 0),
            ]
        ).best(n=n, percent=percent)
        == expected_result
    )


@pytest.mark.parametrize(
    (
        "filename",
        "subclip",
        "match_threshold",
        "min_time_span",
        "nomatch_threshold",
        "expected_result",
    ),
    (
        pytest.param(
            "media/chaplin.mp4",
            (1, 3),
            1,
            2,
            0,
            FramesMatches(
                [
                    FramesMatch(0.08, 2.92, 0, 0),
                    FramesMatch(0.2, 2.8, 0, 0),
                    FramesMatch(0.32, 2.68, 0, 0),
                    FramesMatch(0.44, 2.56, 0, 0),
                ]
            ),
            id="(media/chaplin.mp4)(1, 3).fx(time_mirror)",
        ),
    ),
)
def test_FramesMatches_select_scenes(
    filename,
    subclip,
    match_threshold,
    min_time_span,
    nomatch_threshold,
    expected_result,
):
    video_clip = VideoFileClip(filename)
    if subclip is not None:
        video_clip = video_clip.subclip(subclip[0], subclip[1])
    clip = concatenate_videoclips([video_clip.fx(time_mirror), video_clip])
    result = FramesMatches.from_clip(clip, 10, 3, logger=None).select_scenes(
        match_threshold,
        min_time_span,
        nomatch_threshold=nomatch_threshold,
    )

    assert len(result) == len(expected_result)
    assert result == expected_result


def test_FramesMatches_write_gifs():
    video_clip = VideoFileClip("media/chaplin.mp4").subclip(0, 0.2)
    clip = concatenate_videoclips([video_clip.fx(time_mirror), video_clip])

    # add matching frame starting at start < clip.start which should be ignored
    matching_frames = FramesMatches.from_clip(clip, 10, 3, logger=None)
    matching_frames.insert(0, FramesMatch(-1, -0.5, 0, 0))
    matching_frames = matching_frames.select_scenes(
        1,
        0.01,
        nomatch_threshold=0,
    )

    gifs_dir = os.path.join(TMP_DIR, "moviepy_FramesMatches_write_gifs")
    if os.path.isdir(gifs_dir):
        shutil.rmtree(gifs_dir)
    os.mkdir(gifs_dir)
    assert os.path.isdir(gifs_dir)

    matching_frames.write_gifs(clip, gifs_dir, logger=None)

    gifs_filenames = os.listdir(gifs_dir)
    assert len(gifs_filenames) == 7

    for filename in gifs_filenames:
        filepath = os.path.join(gifs_dir, filename)
        assert os.path.isfile(filepath)

        with open(filepath, "rb") as f:
            assert len(f.readline())

        end, start = filename.split(".")[0].split("_")
        end, start = (int(end), int(start))
        assert isinstance(end, int)
        assert isinstance(end, int)

    shutil.rmtree(gifs_dir)


@pytest.mark.parametrize(
    (
        "size",
        "p1",
        "p2",
        "vector",
        "radius",
        "color_1",
        "color_2",
        "shape",
        "offset",
        "expected_result",
    ),
    (
        pytest.param(
            (6, 1),
            (1, 1),
            (5, 1),
            None,
            None,
            0,
            1,
            "linear",
            0,
            np.array([[1.0, 1.0, 0.75, 0.5, 0.25, 0.0]]),
            id="p1-p2-linear-color_1=0-color_2=1",
        ),
        pytest.param(
            (6, 1),
            (1, 1),
            None,
            (4, 0),
            None,
            0,
            1,
            "linear",
            0,
            np.array([[1.0, 1.0, 0.75, 0.5, 0.25, 0.0]]),
            id="p1-vector-linear-color_1=0-color_2=1",
        ),
        pytest.param(
            (6, 1),
            (1, 1),
            (5, 1),
            None,
            None,
            (255, 0, 0),
            (0, 255, 0),
            "linear",
            0,
            np.array(
                [
                    [
                        [
                            0,
                            255,
                            0,
                        ],
                        [
                            0,
                            255,
                            0,
                        ],
                        [
                            63.75,
                            191.25,
                            0,
                        ],
                        [
                            127.5,
                            127.5,
                            0,
                        ],
                        [
                            191.25,
                            63.75,
                            0,
                        ],
                        [
                            255,
                            0,
                            0,
                        ],
                    ]
                ]
            ),
            id="p1-p2-linear-color_1=R-color_2=G",
        ),
        pytest.param(
            (3, 1),
            (1, 1),
            (5, 1),
            None,
            None,
            0,
            1,
            "bilinear",
            0,
            np.array([[0.75, 1, 0.75]]),
            id="p1-p2-bilinear-color_1=0-color_2=1",
        ),
        pytest.param(
            (5, 1),
            (1, 1),
            (3, 1),
            None,
            None,
            0,
            1,
            "bilinear",
            0,
            np.array([[0.5, 1.0, 0.5, 0.0, 0.0]]),
            id="p1-p2-bilinear-color_1=0-color_2=1",
        ),
        pytest.param(
            (5, 1),
            (1, 1),
            None,
            [2, 0],
            None,
            0,
            1,
            "bilinear",
            0,
            np.array([[0.5, 1.0, 0.5, 0.0, 0.0]]),
            id="p1-vector-bilinear-color_1=0-color_2=1",
        ),
        pytest.param(
            (5, 1),
            (1, 1),
            None,
            [2, 0],
            None,
            (255, 0, 0),
            (0, 255, 0),
            "bilinear",
            0,
            np.array(
                [
                    [
                        [127.5, 127.5, 0],
                        [0, 255, 0],
                        [127.5, 127.5, 0],
                        [255, 0, 0],
                        [255, 0, 0],
                    ]
                ]
            ),
            id="p1-vector-bilinear-color_1=R-color_2=G",
        ),
        pytest.param(
            (5, 1),
            (1, 1),
            None,
            None,
            None,
            0,
            1,
            "bilinear",
            0,
            (ValueError, "You must provide either 'p2' or 'vector'"),
            id="p2=None-vector=None-bilinear-ValueError",
        ),
        pytest.param(
            (5, 1),
            (1, 1),
            None,
            None,
            None,
            0,
            1,
            "linear",
            0,
            (ValueError, "You must provide either 'p2' or 'vector'"),
            id="p2=None-vector=None-linear-ValueError",
        ),
        pytest.param(
            (5, 1),
            (1, 1),
            None,
            None,
            None,
            0,
            1,
            "invalid",
            0,
            (
                ValueError,
                "Invalid shape, should be either 'radial', 'linear' or 'bilinear'",
            ),
            id="shape=invalid-ValueError",
        ),
        pytest.param(
            (5, 5),
            (1, 1),
            None,
            None,
            1,
            0,
            1,
            "radial",
            0,
            np.array(
                [
                    [1, 1, 1, 1, 1],
                    [1, 0, 1, 1, 1],
                    [1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1],
                ]
            ),
            id="p1-radial-radius=1-color_1=0-color_2=1",
        ),
        pytest.param(
            (5, 5),
            (1, 1),
            None,
            None,
            1,
            (255, 0, 0),
            (0, 255, 0),
            "radial",
            0,
            np.array(
                [
                    [[0, 255, 0], [0, 255, 0], [0, 255, 0], [0, 255, 0], [0, 255, 0]],
                    [[0, 255, 0], [255, 0, 0], [0, 255, 0], [0, 255, 0], [0, 255, 0]],
                    [[0, 255, 0], [0, 255, 0], [0, 255, 0], [0, 255, 0], [0, 255, 0]],
                    [[0, 255, 0], [0, 255, 0], [0, 255, 0], [0, 255, 0], [0, 255, 0]],
                    [[0, 255, 0], [0, 255, 0], [0, 255, 0], [0, 255, 0], [0, 255, 0]],
                ]
            ),
            id="p1-radial-radius=1-color_1=R-color_2=G",
        ),
        pytest.param(
            (5, 5),
            (3, 3),
            None,
            None,
            0,
            0,
            1,
            "radial",
            0,
            np.array(
                [
                    [1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1],
                    [1, 1, 1, 1, 1],
                ]
            ),
            id="p1-radial-radius=0-color_1=0-color_2=1",
        ),
    ),
)
def test_color_gradient(
    size,
    p1,
    p2,
    vector,
    radius,
    color_1,
    color_2,
    shape,
    offset,
    expected_result,
):
    if isinstance(expected_result, np.ndarray):
        result = color_gradient(
            size,
            p1,
            p2=p2,
            vector=vector,
            radius=radius,
            color_1=color_1,
            color_2=color_2,
            shape=shape,
            offset=offset,
        )

        assert expected_result.shape == result.shape
        assert np.array_equal(result, expected_result)

        if shape == "radial":

            circle_result = circle(
                size,
                p1,
                radius,
                color=color_1,
                bg_color=color_2,
            )
            assert np.array_equal(result, circle_result)
    else:
        if isinstance(expected_result, (list, tuple)):
            expected_error, expected_message = expected_result
        else:
            expected_error, expected_message = (expected_result, None)

        with pytest.raises(expected_error) as exc:
            color_gradient(
                size,
                p1,
                p2=p2,
                vector=vector,
                radius=radius,
                color_1=color_1,
                color_2=color_2,
                shape=shape,
                offset=offset,
            )
        if expected_message is not None:
            assert str(exc.value) == expected_message


@pytest.mark.parametrize(
    (
        "size",
        "x",
        "y",
        "p1",
        "p2",
        "vector",
        "color_1",
        "color_2",
        "gradient_width",
        "expected_result",
    ),
    (
        pytest.param(
            (3, 4),
            1,
            None,
            None,
            None,
            None,
            (255, 0, 0),
            (0, 255, 0),
            0,
            np.array(
                [
                    [[255, 0, 0], [0, 255, 0], [0, 255, 0]],
                    [[255, 0, 0], [0, 255, 0], [0, 255, 0]],
                    [[255, 0, 0], [0, 255, 0], [0, 255, 0]],
                    [[255, 0, 0], [0, 255, 0], [0, 255, 0]],
                ]
            ),
            id="x=1-color_1=R-color_2=G",
        ),
        pytest.param(
            (3, 4),
            1,
            None,
            None,
            None,
            None,
            0,
            1,
            0,
            np.array([[0, 1, 1], [0, 1, 1], [0, 1, 1], [0, 1, 1]]),
            id="x=1-color_1=0-color_2=1",
        ),
        pytest.param(
            (2, 2),
            None,
            1,
            None,
            None,
            None,
            (255, 0, 0),
            (0, 255, 0),
            0,
            np.array([[[255, 0, 0], [255, 0, 0]], [[0, 255, 0], [0, 255, 0]]]),
            id="y=1-color_1=R-color_2=G",
        ),
        pytest.param(
            (2, 2),
            None,
            1,
            None,
            None,
            None,
            0,
            1,
            0,
            np.array([[0, 0], [1, 1]]),
            id="y=1-color_1=0-color_2=1",
        ),
        pytest.param(
            (3, 2),
            2,
            None,
            None,
            None,
            None,
            0,
            1,
            1,
            np.array([[0, 0, 1], [0, 0, 1]]),
            id="x=2-color_1=0-color_2=1-gradient_width=1",
        ),
        pytest.param(
            (2, 3),
            None,
            2,
            None,
            None,
            None,
            0,
            1,
            1,
            np.array([[0, 0], [0, 0], [1, 1]]),
            id="y=2-color_1=0-color_2=1-gradient_width=1",
        ),
        pytest.param(
            (3, 3),
            None,
            None,
            (0, 1),
            (0, 0),
            None,
            0,
            0.75,
            3,
            np.array([[0.75, 0.75, 0.75], [0.75, 0.75, 0.75], [0.75, 0.75, 0.75]]),
            id="p1-p2-color_1=0-color_2=0.75-gradient_width=3",
        ),
    ),
)
def test_color_split(
    size,
    x,
    y,
    p1,
    p2,
    vector,
    color_1,
    color_2,
    gradient_width,
    expected_result,
):
    result = color_split(
        size,
        x=x,
        y=y,
        p1=p1,
        p2=p2,
        vector=vector,
        color_1=color_1,
        color_2=color_2,
        gradient_width=gradient_width,
    )

    assert np.array_equal(result, expected_result)


@pytest.mark.parametrize(
    ("clip", "filetype", "fps", "maxduration", "t", "expected_error"),
    (
        pytest.param(
            AudioClip(get_stereo_wave(), duration=0.2, fps=44100),
            None,
            None,
            None,
            None,
            None,
            id="AudioClip",
        ),
        pytest.param(
            VideoFileClip("media/bitmap.mp4"),
            None,
            None,
            None,
            None,
            None,
            id="VideoFileClip",
        ),
        pytest.param(
            BitmapClip([["RR", "RR"], ["GG", "GG"]], duration=0.25),
            None,
            4,
            None,
            None,
            None,
            id="BitmapClip",
        ),
        pytest.param(
            ImageClip("media/python_logo.png"),
            None,
            None,
            None,
            None,
            None,
            id="ImageClip(.png)",
        ),
        pytest.param(
            ImageClip("media/pigs_in_a_polka.gif"),
            None,
            None,
            None,
            None,
            None,
            id="ImageClip(.gif)",
        ),
        pytest.param(
            os.path.join("media", "pigs_in_a_polka.gif"),
            None,
            None,
            None,
            None,
            None,
            id="filename(.gif)",
        ),
        pytest.param(
            os.path.join("media", "vacation_2017.jpg"),
            None,
            None,
            None,
            None,
            None,
            id="filename(.jpg)",
        ),
        pytest.param(
            os.path.join(TMP_DIR, "moviepy_ipython_display.foo"),
            None,  # unknown filetype
            None,
            None,
            None,
            (ValueError, "No file type is known for the provided file."),
            id="filename(.foo)",
        ),
        pytest.param(
            os.path.join(TMP_DIR, "moviepy_ipython_display.foo"),
            "video",  # unsupported filetype for '.foo' extension
            None,
            None,
            None,
            (
                ValueError,
                "This video extension cannot be displayed in the IPython Notebook.",
            ),
            id="filename(.foo)[filetype=video]",
        ),
        pytest.param(
            VideoFileClip("media/bitmap.mp4"),
            "video",
            None,
            0,
            None,
            (
                ValueError,
                "You can increase 'maxduration', by passing 'maxduration'",
            ),
            id="VideoFileClip(.mp4)[filetype=video, maxduration > clip.duration]",
        ),
        pytest.param(
            type("FakeClip", (), {})(),
            None,
            None,
            None,
            None,
            (ValueError, "Unknown class for the clip. Cannot embed and preview"),
            id="FakeClip",
        ),
        pytest.param(
            VideoFileClip("media/chaplin.mp4").subclip(0, 1),
            None,
            None,
            None,
            0.5,
            None,
            id="VideoFileClip(.mp4)[filetype=video, t=0.5]",
        ),
        pytest.param(
            ImageClip("media/pigs_in_a_polka.gif"),
            None,
            None,
            None,
            0.2,
            None,
            id="ImageClip(.gif)[t=0.2]",
        ),
    ),
)
def test_ipython_display(
    clip, filetype, fps, maxduration, t, expected_error, monkeypatch
):
    # patch module to use it without ipython installed
    video_io_html_tools_module = importlib.import_module("moviepy.video.io.html_tools")
    monkeypatch.setattr(video_io_html_tools_module, "ipython_available", True)

    # build `ipython_display` kwargs
    kwargs = {}
    if fps is not None:
        kwargs["fps"] = fps
    if maxduration is not None:
        kwargs["maxduration"] = maxduration
    if t is not None:
        kwargs["t"] = t

    if expected_error is None:
        html_content = video_io_html_tools_module.ipython_display(
            clip,
            rd_kwargs=dict(logger=None),
            filetype=filetype,
            **kwargs,
        )
    else:
        with pytest.raises(expected_error[0]) as exc:
            video_io_html_tools_module.ipython_display(
                clip,
                rd_kwargs=None if not kwargs else dict(logger=None),
                filetype=filetype,
                **kwargs,
            )
        assert expected_error[1] in str(exc.value)
        return

    # assert built content according to each file type
    HTML5_support_message = (
        "Sorry, seems like your browser doesn't support HTML5 audio/video"
    )

    def image_contents():
        return ("<div align=middle><img  src=", "></div>")

    if isinstance(clip, AudioClip):
        content_start = "<div align=middle><audio controls><source   src="
        content_end = f">{HTML5_support_message}</audio></div>"
    elif isinstance(clip, ImageClip) or t is not None:  # t -> ImageClip
        content_start, content_end = image_contents()
    elif isinstance(clip, VideoClip):
        content_start = "<div align=middle><video src="
        content_end = f" controls>{HTML5_support_message}</video></div>"
    else:
        ext = os.path.splitext(clip)[1]
        if ext in [".jpg", ".gif"]:
            content_start, content_end = image_contents()
        else:
            raise NotImplementedError(
                f"'test_ipython_display' must handle '{ext}' extension types!"
            )

    assert html_content.startswith(content_start)
    assert html_content.endswith(content_end)

    # clean `ipython` and `moviepy.video.io.html_tools` module from cache
    del sys.modules["moviepy.video.io.html_tools"]
    if "ipython" in sys.modules:
        del sys.modules["ipython"]


@pytest.mark.skipif(
    ipython_available,
    reason="ipython must not be installed in order to run this test",
)
def test_ipython_display_not_available():
    video_io_html_tools_module = importlib.import_module("moviepy.video.io.html_tools")

    with pytest.raises(ImportError) as exc:
        video_io_html_tools_module.ipython_display("foo")
    assert str(exc.value) == "Only works inside an IPython Notebook"

    del sys.modules["moviepy.video.io.html_tools"]


@pytest.mark.parametrize("wave", ("mono", "stereo"))
def test_find_audio_period(wave):
    if wave == "mono":
        wave1 = get_mono_wave(freq=400)
        wave2 = get_mono_wave(freq=100)
    else:
        wave1 = get_stereo_wave(left_freq=400, right_freq=220)
        wave2 = get_stereo_wave(left_freq=100, right_freq=200)
    clip = CompositeAudioClip(
        [
            AudioClip(make_frame=wave1, duration=0.3, fps=22050),
            multiply_volume(
                AudioClip(make_frame=wave2, duration=0.3, fps=22050),
                0,
                end_time=0.1,
            ),
        ]
    )
    loop_clip = loop(clip, 4)
    assert round(find_audio_period(loop_clip), 6) == pytest.approx(0.29932, 0.1)


if __name__ == "__main__":
    pytest.main()
