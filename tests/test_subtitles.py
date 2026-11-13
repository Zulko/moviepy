"""Tests for subtitle file output."""

import pytest

from moviepy import ColorClip
from moviepy.video.tools.subtitles import SubtitlesClip, file_to_subtitles


@pytest.mark.parametrize(
    ("start", "end", "expected_start", "expected_end"),
    [
        (0.125, 1.25, "00:00:00,125", "00:00:01,250"),
        (59.9996, 3599.9996, "00:01:00,000", "01:00:00,000"),
        (360000.125, 360001.25, "100:00:00,125", "100:00:01,250"),
    ],
)
def test_write_srt(tmp_path, start, end, expected_start, expected_end):
    subtitles = [((start, end), "First line\nSecond line"), ((end, end + 1), "Next")]
    clip = SubtitlesClip(
        subtitles,
        make_textclip=lambda text: ColorClip((1, 1), color=(0, 0, 0)),
    )
    filename = tmp_path / "subtitles.srt"

    clip.write_srt(filename)

    content = filename.read_text()
    assert content.startswith(
        f"1\n{expected_start} --> {expected_end}\nFirst line\nSecond line\n\n2\n"
    )
    assert content.endswith("\nNext\n\n")
    parsed = file_to_subtitles(filename)
    assert len(parsed) == len(subtitles)
    for (actual_times, actual_text), (times, text) in zip(parsed, subtitles):
        assert actual_times == pytest.approx(times, abs=0.0005)
        assert actual_text == text
