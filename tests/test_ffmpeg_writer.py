"""FFmpeg writer tests of moviepy."""

import os

import pytest
from PIL import Image

from moviepy.video.io.ffmpeg_writer import ffmpeg_write_image
from moviepy.video.tools.drawing import color_gradient

from tests.test_helper import TMP_DIR


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
