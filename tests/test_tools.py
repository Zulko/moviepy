"""Tool tests meant to be run with pytest. Taken from PR #121 (grimley517)."""

import contextlib
import importlib
import io
import os
import shutil
import sys

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
    """Test the convert_to_seconds function outputs correct times as per
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


@pytest.mark.parametrize(
    "given, expected",
    [
        ("-filenamethatstartswithdash-.mp4", "./-filenamethatstartswithdash-.mp4"),
        ("-path/that/starts/with/dash.mp4", "./-path/that/starts/with/dash.mp4"),
        ("file-name-.mp4", "file-name-.mp4"),
        ("/absolute/path/to/-file.mp4", "/absolute/path/to/-file.mp4"),
        ("filename with spaces.mp4", "filename with spaces.mp4"),
    ],
)
def test_ffmpeg_escape_filename(given, expected):
    """Test the ffmpeg_escape_filename function outputs correct paths as per
    the docstring.
    """
    assert tools.ffmpeg_escape_filename(given) == expected


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

    assert len(record) > 0
    assert record[0].message.args[0] == expected_warning_message


@pytest.mark.skipif(os.name != "posix", reason="Doesn't works in Windows")
@pytest.mark.parametrize(
    ("ffmpeg_binary", "ffmpeg_binary_error"),
    (
        pytest.param("ffmpeg-imageio", None, id="FFMPEG_BINARY=ffmpeg-imageio"),
        pytest.param("auto-detect", None, id="FFMPEG_BINARY=auto-detect"),
        pytest.param(
            "foobarbazimpossible",
            (IOError, "No such file or directory:"),
            id="FFMPEG_BINARY=foobarbazimpossible",
        ),
    ),
)
def test_config(
    util,
    ffmpeg_binary,
    ffmpeg_binary_error,
):
    if "moviepy.config" in sys.modules:
        del sys.modules["moviepy.config"]

    if ffmpeg_binary_error is not None and os.path.isfile(ffmpeg_binary):
        os.remove(ffmpeg_binary)
    prev_ffmpeg_binary = os.environ.get("FFMPEG_BINARY")
    os.environ["FFMPEG_BINARY"] = ffmpeg_binary

    if ffmpeg_binary_error is not None:
        with pytest.raises(ffmpeg_binary_error[0]) as exc:
            importlib.import_module("moviepy.config")
        assert ffmpeg_binary_error[1] in str(exc.value)

    if prev_ffmpeg_binary is not None:
        os.environ["FFMPEG_BINARY"] = prev_ffmpeg_binary

    if "moviepy.config" in sys.modules:
        del sys.modules["moviepy.config"]


def test_config_check():
    if "moviepy.config" in sys.modules:
        del sys.modules["moviepy.config"]

    try:
        dotenv_module = importlib.import_module("dotenv")
    except ImportError:
        dotenv_module = None
    else:
        with open(".env", "w") as f:
            f.write("")

    moviepy_config_module = importlib.import_module("moviepy.config")

    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        moviepy_config_module.check()

    output = stdout.getvalue()

    assert "MoviePy: ffmpeg successfully found in" in output

    if dotenv_module:
        assert os.path.isfile(".env")
        os.remove(".env")
        assert ".env file content at" in output
        del sys.modules["dotenv"]

    if "moviepy.config" in sys.modules:
        del sys.modules["moviepy.config"]


@pytest.mark.skipif(sys.version_info < (3, 8), reason="Requires Python 3.8 or greater")
@pytest.mark.parametrize(
    "decorator_name",
    ("convert_parameter_to_seconds", "convert_path_to_string"),
)
def test_decorators_argument_converters_consistency(
    moviepy_modules, functions_with_decorator_defined, decorator_name
):
    """Checks that for all functions that have a decorator defined (like
    ``@convert_parameter_to_seconds``), the parameters passed to the decorator
    correspond to the parameters taken by the function.

    This test is util to prevent next case in which the parameter names doesn't
    match between the decorator and the function definition:

    >>> @convert_parameter_to_seconds(['foo'])
    >>> def whatever_function(bar):  # bar not converted to seconds
    ...     pass

    Some wrong definitions remained unnoticed in the past before this test was
    added.
    """
    with contextlib.redirect_stdout(io.StringIO()):
        for modname, ispkg in moviepy_modules():
            if ispkg:
                continue

            try:
                module = importlib.import_module(modname)
            except ImportError:
                continue

            functions_with_decorator = functions_with_decorator_defined(
                module,
                decorator_name,
            )

            for function_data in functions_with_decorator:
                for argument_name in function_data["decorator_arguments"]:
                    funcname = function_data["function_name"]
                    assert argument_name in function_data["function_arguments"], (
                        f"Wrong argument name '{argument_name}' in"
                        f" '@{decorator_name}' decorator for function"
                        f" '{funcname}' found inside module '{modname}'"
                    )

                assert function_data["decorator_arguments"]
                assert function_data["function_arguments"]


if __name__ == "__main__":
    pytest.main()
