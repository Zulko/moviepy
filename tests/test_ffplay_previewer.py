"""FFplay video previewer tests."""

from unittest.mock import MagicMock, patch

import numpy as np

import pytest

from moviepy import BitmapClip
from moviepy.video.io.ffplay_previewer import (
    FFPLAY_VideoPreviewer,
    ffplay_preview_video,
)


def make_ffplay_process(returncode):
    """Build a process mock with the streams used by the previewer."""
    process = MagicMock()
    process.stdin = MagicMock()
    process.stdin.closed = False
    process.stderr = None
    process.returncode = returncode
    process.communicate.return_value = (None, None)
    return process


@patch("moviepy.video.io.ffplay_previewer.sp.Popen")
def test_preview_stops_after_ffplay_closes(popen):
    process = make_ffplay_process(returncode=0)
    process.stdin.write.side_effect = BrokenPipeError("preview window closed")
    popen.return_value = process

    clip = BitmapClip([["R"], ["G"]], fps=1)
    ffplay_preview_video(clip, fps=1)

    assert process.stdin.write.call_count == 1
    process.wait.assert_called_once()


@patch("moviepy.video.io.ffplay_previewer.sp.Popen")
def test_preview_raises_for_ffplay_failure(popen):
    process = make_ffplay_process(returncode=1)
    process.stdin.write.side_effect = BrokenPipeError("ffplay failure")
    popen.return_value = process
    previewer = FFPLAY_VideoPreviewer((1, 1), 1, "rgb24")

    with pytest.raises(IOError, match="FFPLAY encountered"):
        previewer.show_frame(np.zeros((1, 1, 3), dtype="uint8"))

    previewer.close()
    process.wait.assert_called_once()


@patch("moviepy.video.io.ffplay_previewer.sp.Popen")
def test_close_ignores_already_closed_standard_input(popen):
    process = make_ffplay_process(returncode=0)
    process.stdin.closed = True
    popen.return_value = process
    previewer = FFPLAY_VideoPreviewer((1, 1), 1, "rgb24")

    previewer.close()

    process.stdin.close.assert_not_called()
    process.wait.assert_called_once()
