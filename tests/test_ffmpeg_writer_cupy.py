import pytest


def test_ffmpeg_write_image_accepts_cupy(util, monkeypatch):
    cp = pytest.importorskip("cupy")

    from moviepy.video.tools import gpu_render

    if not gpu_render.is_available():
        pytest.skip("CuPy installed but CUDA runtime not usable")

    from moviepy.video.io.ffmpeg_writer import ffmpeg_write_image

    import numpy as np
    import os

    img = np.zeros((8, 9, 3), dtype=np.uint8)
    img[:, :, 0] = 255
    img_cp = cp.asarray(img)

    filename = os.path.join(util.TMP_DIR, "moviepy_ffmpeg_write_image_cupy.png")
    ffmpeg_write_image(filename, img_cp, logfile=False)

    assert os.path.isfile(filename)
