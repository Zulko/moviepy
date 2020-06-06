# -*- coding: utf-8 -*-
"""Tool tests meant to be run with pytest. Taken from PR #121 (grimley517)."""
import sys

import pytest

import moviepy.tools as tools


@pytest.mark.parametrize(
    "given, expected",
    [("libx264", "mp4"), ("libmpeg4", "mp4"), ("libtheora", "ogv"), ("libvpx", "webm")],
)
def test_find_extensions(given, expected):
    """Test for find_extension function."""
    assert tools.find_extension(given) == expected


def test_find_extensions_not_found():
    """Test for raising error if codec not in dictionaries."""
    with pytest.raises(ValueError):  # asking for a silly video format
        tools.find_extension("flashvideo")


@pytest.mark.parametrize(
    "given, expected",
    [
        (15.4, 15.4),
        ((1, 21.5), 81.5),
        ((1, 1, 2), 3662),
        ([1, 1, 2], 3662),
        ("01:01:33.5", 3693.5),
        ("01:01:33.045", 3693.045),
        ("01:01:33,5", 3693.5),
        ("1:33", 93.0),
        ("33.4", 33.4),
        (None, None),
    ],
)
def test_cvsecs(given, expected):
    """Test the cvsecs funtion outputs correct times as per the docstring."""
    assert tools.cvsecs(given) == expected


def test_sys_write_flush():
    """Test for sys_write-flush function. Check that stdout has no content after flushing."""
    tools.sys_write_flush("hello world")

    file = sys.stdout.read()
    assert file == b""


if __name__ == "__main__":
    pytest.main()
