"""Tool tests meant to be run with pytest. Taken from PR #121 (grimley517)."""

import importlib
import os
import shutil

import pytest

import moviepy.tools as tools


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        ("libx264", "mp4"),
        ("libmpeg4", "mp4"),
        ("libtheora", "ogv"),
        ("libvpx", "webm"),
        ("jpeg", "jpeg"),
    ],
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
    """Test the convert_to_seconds funtion outputs correct times as per
    the docstring.
    """
    assert tools.convert_to_seconds(given) == expected


@pytest.mark.skipif(not shutil.which("echo"), reason="not in Unix")
@pytest.mark.parametrize("command", ("echo", "jbdshfuygvhbsdvfghew"))
def test_subprocess_call(command):
    if command == "echo":
        tools.subprocess_call(command, logger=None)
    else:
        with pytest.raises(IOError):
            tools.subprocess_call(command, logger=None)


@pytest.mark.parametrize("os_name", (os.name, "nt"))
def test_cross_platform_popen_params(os_name, monkeypatch):
    tools_module = importlib.import_module("moviepy.tools")
    monkeypatch.setattr(tools_module, "OS_NAME", os_name)

    params = tools_module.cross_platform_popen_params({})
    assert len(params) == (1 if os_name == "nt" else 0)


@pytest.mark.parametrize("old_name", ("bar", "foo"))
def test_deprecated_version_of(old_name):
    def to_file(*args, **kwargs):
        return

    func = tools.deprecated_version_of(to_file, old_name)

    expected_warning_message = (
        f"MoviePy: The function ``{old_name}`` is deprecated and is kept"
        " temporarily for backwards compatibility.\nPlease use the new name"
        f", ``{to_file.__name__}``, instead."
    )

    with pytest.warns(PendingDeprecationWarning) as record:
        func(1, b=2)

    assert len(record) == 1
    assert record[0].message.args[0] == expected_warning_message


if __name__ == "__main__":
    pytest.main()
