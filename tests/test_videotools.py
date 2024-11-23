"""Video file clip tests meant to be run with pytest."""

import importlib
import math
import os
import shutil
import sys

import numpy as np

import pytest

from moviepy import *
from moviepy.audio.tools.cuts import find_audio_period
from moviepy.video.tools.credits import CreditsClip
from moviepy.video.tools.cuts import (
    FramesMatch,
    FramesMatches,
    detect_scenes,
    find_video_period,
)
from moviepy.video.tools.drawing import circle, color_gradient, color_split
from moviepy.video.tools.interpolators import Interpolator, Trajectory


try:
    importlib.import_module("ipython.display")
except ImportError:
    ipython_available = False
else:
    ipython_available = True
    del sys.modules["ipython.display"]


def test_credits(util):
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

    file_location = os.path.join(util.TMP_DIR, "credits.txt")
    vid_location = os.path.join(util.TMP_DIR, "credits.mp4")
    with open(file_location, "w") as file:
        file.write(credit_file)

    image = CreditsClip(
        file_location, 600, gap=100, stroke_color="blue", stroke_width=5, font=util.FONT
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
    clip = (
        VideoFileClip("media/chaplin.mp4")
        .subclipped(0, 0.5)
        .with_effects([vfx.Loop(2)])
    )  # fps=25

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


def test_FramesMatches_save_load(util):
    input_matching_frames = [
        FramesMatch(1, 2, 0, 0),
        FramesMatch(1, 2, 0.8, 0),
        FramesMatch(1, 2, 0.8, 0.8),
    ]
    expected_frames_matches_file_content = """1.000	2.000	0.000	0.000
1.000	2.000	0.800	0.000
1.000	2.000	0.800	0.800
"""

    outputfile = os.path.join(util.TMP_DIR, "moviepy_FramesMatches_save_load.txt")

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
        video_clip = video_clip.subclipped(subclip[0], subclip[1])
    clip = concatenate_videoclips(
        [video_clip.with_effects([vfx.TimeMirror()]), video_clip]
    )
    result = FramesMatches.from_clip(clip, 10, 3, logger=None).select_scenes(
        match_threshold,
        min_time_span,
        nomatch_threshold=nomatch_threshold,
    )

    assert len(result) == len(expected_result)
    assert result == expected_result


def test_FramesMatches_write_gifs(util):
    video_clip = VideoFileClip("media/chaplin.mp4").subclipped(0, 0.2)
    clip = concatenate_videoclips(
        [video_clip.with_effects([vfx.TimeMirror()]), video_clip]
    )

    # add matching frame starting at start < clip.start which should be ignored
    matching_frames = FramesMatches.from_clip(clip, 10, 3, logger=None)
    matching_frames.insert(0, FramesMatch(-1, -0.5, 0, 0))
    matching_frames = matching_frames.select_scenes(
        1,
        0.01,
        nomatch_threshold=0,
    )

    gifs_dir = os.path.join(util.TMP_DIR, "moviepy_FramesMatches_write_gifs")
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

    try:
        shutil.rmtree(gifs_dir)
    except PermissionError:
        pass


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
    ("ttss", "tt", "ss", "left", "right", "interpolation_results"),
    (
        pytest.param(
            [[0, 3], [1, 4], [2, 5]],
            None,
            None,
            -1,
            6,
            {
                3: 6,
                4: 6,  # right
                -1: -1,
                -2: -1,  # left
                1: 4,
                2: 5,  # values
            },
            id="ttss",
        ),
        pytest.param(
            None,
            [0, 1, 2],
            [3, 4, 5],
            -1,
            39,
            {
                3: 39,
                4: 39,  # right
                -1: -1,
                -2: -1,  # left
                1: 4,
                2: 5,  # values
            },
            id="tt-ss",
        ),
    ),
)
def test_Interpolator(ttss, tt, ss, left, right, interpolation_results):
    interpolator = Interpolator(ttss=ttss, tt=tt, ss=ss, left=left, right=right)
    for value, expected_result in interpolation_results.items():
        assert interpolator(value) == expected_result


@pytest.mark.parametrize(
    ("tt", "xx", "yy", "interpolation_results"),
    (
        pytest.param(
            [0, 1, 2],
            [0, 2, 3],
            [0, 2, 3],
            {0.5: [1, 1], 1: [2, 2], 4: [3, 3], -1: [0, 0]},
            id="simple",
        ),
        pytest.param(
            [0, 1, 2],
            [0, -5, -3],
            [-2, 2, -5],
            {0.5: [-2.5, 0], 1: [-5, 2], 4: [-3, -5], -1: [0, -2]},
            id="negative",
        ),
    ),
)
def test_Trajectory(tt, xx, yy, interpolation_results):
    trajectory = Trajectory(tt, xx, yy)
    for value, expected_result in interpolation_results.items():
        assert np.array_equal(trajectory(value), np.array(expected_result))


def test_Trajectory_addx():
    trajectory = Trajectory([0, 1], [0], [0, 1]).addx(1)
    assert len(trajectory.xx) == 1
    assert trajectory.xx[0] == 1


def test_Trajectory_addy():
    trajectory = Trajectory([0, 1], [0], [0, 1]).addy(1)
    assert len(trajectory.yy) == 2
    assert trajectory.yy[0] == 1
    assert trajectory.yy[1] == 2


def test_Trajectory_from_to_file(util):
    filename = os.path.join(util.TMP_DIR, "moviepy_Trajectory_from_to_file.txt")
    if os.path.isfile(filename):
        try:
            os.remove(filename)
        except PermissionError:
            pass

    trajectory_file_content = """# t(ms)	x	y
0	554	100
166	474	90
333	384	91
"""

    with open(filename, "w") as f:
        f.write(trajectory_file_content)

    trajectory = Trajectory.from_file(filename)

    assert np.array_equal(trajectory.xx, np.array([554, 474, 384]))
    assert np.array_equal(trajectory.yy, np.array([100, 90, 91]))
    assert np.array_equal(trajectory.tt, np.array([0, 0.166, 0.333]))

    trajectory.to_file(filename)

    with open(filename, "r") as f:
        assert f.read() == "\n".join(trajectory_file_content.split("\n")[1:])


@pytest.mark.parametrize(
    ("clip", "filetype", "fps", "maxduration", "t", "expected_error"),
    (
        pytest.param(
            AudioClip(
                lambda t: np.array(
                    [np.sin(440 * 2 * np.pi * t), np.sin(220 * 2 * np.pi * t)]
                ).T.copy(order="C"),
                duration=0.2,
                fps=44100,
            ),
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
            ImageClip(os.path.join("media", "pigs_in_a_polka.gif")),
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
            os.path.join("{tempdir}", "moviepy_ipython_display.foo"),
            None,  # unknown filetype
            None,
            None,
            None,
            (ValueError, "No file type is known for the provided file."),
            id="filename(.foo)",
        ),
        pytest.param(
            os.path.join("{tempdir}", "moviepy_ipython_display.foo"),
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
            VideoFileClip("media/chaplin.mp4").subclipped(0, 1),
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
    util, clip, filetype, fps, maxduration, t, expected_error, monkeypatch
):
    # TODO: fix ipython tests
    pass


@pytest.mark.skipif(
    ipython_available,
    reason="ipython must not be installed in order to run this test",
)
def test_ipython_display_not_available():
    # TODO: fix ipython tests
    pass


@pytest.mark.parametrize("wave_type", ("mono", "stereo"))
def test_find_audio_period(mono_wave, stereo_wave, wave_type):
    if wave_type == "mono":
        wave1 = mono_wave(freq=400)
        wave2 = mono_wave(freq=100)
    else:
        wave1 = stereo_wave(left_freq=400, right_freq=220)
        wave2 = stereo_wave(left_freq=100, right_freq=200)
    clip = CompositeAudioClip(
        [
            AudioClip(frame_function=wave1, duration=0.3, fps=22050),
            AudioClip(frame_function=wave2, duration=0.3, fps=22050).with_effects(
                [afx.MultiplyVolume(0, end_time=0.1)]
            ),
        ]
    )

    loop_clip = clip.with_effects([vfx.Loop(4)])
    assert round(find_audio_period(loop_clip), 6) == pytest.approx(0.29932, 0.1)


if __name__ == "__main__":
    pytest.main()
