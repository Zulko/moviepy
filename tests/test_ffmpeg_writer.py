"""FFmpeg writer tests of moviepy."""

import multiprocessing
import os

import pytest
from PIL import Image

from moviepy.video.io.ffmpeg_writer import ffmpeg_write_image, ffmpeg_write_video
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.tools.drawing import color_gradient
from moviepy.video.VideoClip import BitmapClip

from tests.test_helper import TMP_DIR


@pytest.mark.parametrize(
    "with_mask",
    (False, True),
    ids=("with_mask=False", "with_mask=True"),
)
@pytest.mark.parametrize(
    "write_logfile",
    (False, True),
    ids=("write_logfile=False", "write_logfile=True"),
)
@pytest.mark.parametrize(
    ("codec", "is_valid_codec", "ext"),
    (
        pytest.param(
            "libcrazyfoobar", False, ".mp4", id="codec=libcrazyfoobar-ext=.mp4"
        ),
        pytest.param(None, True, ".mp4", id="codec=default-ext=.mp4"),
        pytest.param("libtheora", False, ".avi", id="codec=libtheora-ext=.mp4"),
    ),
)
@pytest.mark.parametrize(
    "bitrate",
    (None, "5000k"),
    ids=("bitrate=None", "bitrate=5000k"),
)
@pytest.mark.parametrize(
    "threads",
    (None, multiprocessing.cpu_count()),
    ids=("threads=None", "threads=multiprocessing.cpu_count()"),
)
def test_ffmpeg_write_video(
    codec,
    is_valid_codec,
    ext,
    write_logfile,
    with_mask,
    bitrate,
    threads,
):
    filename = os.path.join(TMP_DIR, f"moviepy_ffmpeg_write_video{ext}")
    if os.path.isfile(filename):
        os.remove(filename)

    logfile_name = filename + ".log"
    if os.path.isfile(logfile_name):
        os.remove(logfile_name)

    clip = BitmapClip([["R"], ["G"], ["B"]], fps=10).with_duration(0.3)
    if with_mask:
        clip = clip.with_mask(
            BitmapClip([["W"], ["O"], ["O"]], fps=10, is_mask=True).with_duration(0.3)
        )

    kwargs = dict(
        logger=None,
        write_logfile=write_logfile,
        with_mask=with_mask,
    )
    if codec is not None:
        kwargs["codec"] = codec
    if bitrate is not None:
        kwargs["bitrate"] = bitrate
    if threads is not None:
        kwargs["threads"] = threads

    ffmpeg_write_video(clip, filename, 10, **kwargs)

    if is_valid_codec:
        assert os.path.isfile(filename)

        final_clip = VideoFileClip(filename)

        r, g, b = final_clip.get_frame(0)[0][0]
        assert r == 254
        assert g == 0
        assert b == 0

        r, g, b = final_clip.get_frame(0.1)[0][0]
        assert r == (0 if not with_mask else 1)
        assert g == (255 if not with_mask else 1)
        assert b == 1

        r, g, b = final_clip.get_frame(0.2)[0][0]
        assert r == 0
        assert g == 0
        assert b == (255 if not with_mask else 0)

    if write_logfile:
        assert os.path.isfile(logfile_name)


@pytest.mark.parametrize(
    ("size", "logfile", "pixel_format", "expected_result"),
    (
        pytest.param(
            (5, 1),
            False,
            None,
            [[(0, 255, 0), (51, 204, 0), (102, 153, 0), (153, 101, 0), (204, 50, 0)]],
            id="size=(5, 1)",
        ),
        pytest.param(
            (2, 1), False, None, [[(0, 255, 0), (51, 204, 0)]], id="size=(2, 1)"
        ),
        pytest.param(
            (2, 1), True, None, [[(0, 255, 0), (51, 204, 0)]], id="logfile=True"
        ),
        pytest.param(
            (2, 1),
            False,
            "invalid",
            (OSError, "MoviePy error: FFMPEG encountered the following error"),
            id="pixel_format=invalid-OSError",
        ),
    ),
)
def test_ffmpeg_write_image(size, logfile, pixel_format, expected_result):
    filename = os.path.join(TMP_DIR, "moviepy_ffmpeg_write_image.png")
    if os.path.isfile(filename):
        os.remove(filename)

    image_array = color_gradient(
        size,
        (0, 0),
        p2=(5, 0),
        color_1=(255, 0, 0),
        color_2=(0, 255, 0),
    )

    if hasattr(expected_result[0], "__traceback__"):
        with pytest.raises(expected_result[0]) as exc:
            ffmpeg_write_image(
                filename,
                image_array,
                logfile=logfile,
                pixel_format=pixel_format,
            )
        assert expected_result[1] in str(exc.value)
        return
    else:
        ffmpeg_write_image(
            filename,
            image_array,
            logfile=logfile,
            pixel_format=pixel_format,
        )

    assert os.path.isfile(filename)

    if logfile:
        assert os.path.isfile(filename + ".log")
        os.remove(filename + ".log")

    im = Image.open(filename, mode="r")
    for i in range(im.width):
        for j in range(im.height):
            assert im.getpixel((i, j)) == expected_result[j][i]
