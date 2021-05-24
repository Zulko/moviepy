"""Moviepy editor tests."""

import importlib
import io
from contextlib import redirect_stdout

import pytest

from moviepy.audio.AudioClip import AudioClip
from moviepy.video.VideoClip import VideoClip


def test_preview_methods():
    stdout = io.StringIO()
    with redirect_stdout(stdout):
        try:
            preview_module = importlib.import_module("moviepy.video.io.preview")
            assert preview_module.preview.__hash__() != VideoClip.preview.__hash__()
        except ImportError:
            editor_module = importlib.import_module("moviepy.editor")
            with pytest.raises(ImportError) as exc:
                VideoClip.preview(True)
            assert str(exc.value) == "clip.preview requires Pygame installed"

            with pytest.raises(ImportError) as exc:
                VideoClip.show(True)
            assert str(exc.value) == "clip.show requires Pygame installed"

            with pytest.raises(ImportError) as exc:
                AudioClip.preview(True)
            assert str(exc.value) == "clip.preview requires Pygame installed"
        else:
            editor_module = importlib.import_module("moviepy.editor")
            assert (
                editor_module.VideoClip.preview.__hash__()
                == preview_module.preview.__hash__()
            )

        try:
            importlib.import_module("matplotlib")
        except ImportError:
            editor_module = importlib.import_module("moviepy.editor")
            with pytest.raises(ImportError) as exc:
                editor_module.sliders()

            assert str(exc.value) == "sliders requires matplotlib installed"


if __name__ == "__main__":
    pytest.main()
