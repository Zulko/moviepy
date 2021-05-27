"""Video file clip tests meant to be run with pytest."""

import importlib
import math
import os
import sys

import pytest

from moviepy.audio.AudioClip import AudioClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.tools.credits import CreditsClip
from moviepy.video.tools.cuts import (
    FramesMatch,
    FramesMatches,
    detect_scenes,
    find_video_period,
)
from moviepy.video.VideoClip import BitmapClip, ColorClip, ImageClip, VideoClip

from tests.test_helper import FONT, TMP_DIR, get_stereo_wave


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


if __name__ == "__main__":
    pytest.main()
