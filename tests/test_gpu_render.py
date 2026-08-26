import numpy as np
import pytest


def test_gpu_render_composite_smoke(monkeypatch):
    cp = pytest.importorskip("cupy")

    monkeypatch.setenv("MOVIEPY_GPU_RENDER", "1")
    monkeypatch.setenv("MOVIEPY_GPU_AGGRESSIVE", "1")
    monkeypatch.setenv("MOVIEPY_GPU_RENDER_STRICT", "1")

    from moviepy.video.VideoClip import ColorClip
    from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
    from moviepy.video.tools import gpu_render

    if not gpu_render.is_available():
        pytest.skip("CuPy installed but CUDA runtime not usable")

    base = ColorClip((64, 48), color=(10, 20, 30)).with_duration(1).with_fps(5)
    top = ColorClip((20, 10), color=(200, 0, 0)).with_duration(1).with_fps(5)
    top = top.with_position((5, 7))

    comp = CompositeVideoClip([base, top], size=(64, 48), bg_color=(0, 0, 0))

    frame_gpu = gpu_render.get_frame_for_export_uint8_gpu(comp, 0)
    # In GPU mode and with a CUDA device, we expect a CuPy array.
    assert hasattr(frame_gpu, "__cuda_array_interface__")

    frame = cp.asnumpy(frame_gpu)
    assert isinstance(frame, np.ndarray)
    assert frame.dtype == np.uint8
    assert frame.shape == (48, 64, 3)


def test_gpu_render_transform_fadein_smoke(monkeypatch):
    cp = pytest.importorskip("cupy")

    monkeypatch.setenv("MOVIEPY_GPU_RENDER", "1")
    monkeypatch.setenv("MOVIEPY_GPU_AGGRESSIVE", "1")
    monkeypatch.setenv("MOVIEPY_GPU_RENDER_STRICT", "1")

    from moviepy.video.VideoClip import ColorClip
    from moviepy.video.fx.FadeIn import FadeIn
    from moviepy.video.tools import gpu_render

    if not gpu_render.is_available():
        pytest.skip("CuPy installed but CUDA runtime not usable")

    clip = (
        ColorClip((32, 24), color=(10, 20, 30))
        .with_duration(1)
        .with_fps(5)
        .with_effects([FadeIn(0.5)])
    )

    # Ensure the GPU compositor is actually using the internal GPU frame path.
    called = {"n": 0}
    orig = getattr(clip, "_gpu_frame_function", None)
    assert orig is not None

    def wrapped(t):
        called["n"] += 1
        return orig(t)

    clip._gpu_frame_function = wrapped

    frame_gpu = gpu_render.get_frame_for_export_uint8_gpu(clip, 0.1)
    assert called["n"] > 0

    assert hasattr(frame_gpu, "__cuda_array_interface__")
    frame = cp.asnumpy(frame_gpu)
    assert frame.dtype == np.uint8
    assert frame.shape == (24, 32, 3)
    assert frame[0, 0].tolist() == [2, 4, 6]


def test_gpu_render_composite_mask_is_composited_on_gpu(monkeypatch):
    cp = pytest.importorskip("cupy")

    monkeypatch.setenv("MOVIEPY_GPU_RENDER", "1")
    monkeypatch.setenv("MOVIEPY_GPU_AGGRESSIVE", "1")
    monkeypatch.setenv("MOVIEPY_GPU_RENDER_STRICT", "1")

    from moviepy.video.VideoClip import ColorClip
    from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
    from moviepy.video.tools import gpu_render

    if not gpu_render.is_available():
        pytest.skip("CuPy installed but CUDA runtime not usable")

    top = ColorClip((20, 10), color=(200, 0, 0)).with_duration(1).with_fps(5)
    top = top.with_position((5, 7))

    # Transparent composite -> has a CompositeVideoClip mask.
    comp = CompositeVideoClip([top], size=(64, 48), bg_color=None)
    assert comp.mask is not None
    assert isinstance(comp.mask, CompositeVideoClip)
    assert comp.mask.is_mask

    # Ensure GPU export doesn't call comp.mask.get_frame() / frame_function.
    comp.mask.frame_function = lambda t: (_ for _ in ()).throw(
        RuntimeError("mask frame_function should not be called in GPU path")
    )

    frame_gpu = gpu_render.get_frame_for_export_uint8_gpu(comp, 0)
    assert hasattr(frame_gpu, "__cuda_array_interface__")

    frame = cp.asnumpy(frame_gpu)
    assert frame.dtype == np.uint8
    assert frame.shape == (48, 64, 4)
    # Outside mask should be transparent.
    assert frame[0, 0].tolist() == [0, 0, 0, 0]
    # Inside the top clip region alpha should be fully opaque.
    assert frame[10, 10, 3] == 255


def test_gpu_render_effects_lum_gamma_smoke(monkeypatch):
    cp = pytest.importorskip("cupy")

    monkeypatch.setenv("MOVIEPY_GPU_RENDER", "1")
    monkeypatch.setenv("MOVIEPY_GPU_AGGRESSIVE", "1")
    monkeypatch.setenv("MOVIEPY_GPU_RENDER_STRICT", "1")

    import numpy as np

    from moviepy.video.VideoClip import VideoClip
    from moviepy.video.fx.GammaCorrection import GammaCorrection
    from moviepy.video.fx.LumContrast import LumContrast
    from moviepy.video.tools import gpu_render

    if not gpu_render.is_available():
        pytest.skip("CuPy installed but CUDA runtime not usable")

    def frame_function(_t):
        frame = np.empty((12, 16, 3), dtype=np.uint8)
        frame[...] = (100, 150, 200)
        return frame

    clip = VideoClip(frame_function=frame_function, duration=1).with_fps(5)
    clip = clip.with_effects([LumContrast(lum=10, contrast=0.2), GammaCorrection(gamma=0.8)])

    called = {"n": 0}
    orig = getattr(clip, "_gpu_frame_function", None)
    assert orig is not None

    def wrapped(t):
        called["n"] += 1
        return orig(t)

    clip._gpu_frame_function = wrapped

    frame_gpu = gpu_render.get_frame_for_export_uint8_gpu(clip, 0)
    assert called["n"] > 0
    assert hasattr(frame_gpu, "__cuda_array_interface__")

    frame = cp.asnumpy(frame_gpu)
    assert frame.dtype == np.uint8
    assert frame.shape == (12, 16, 3)


def test_gpu_render_nested_composite_does_not_call_inner_get_frame(monkeypatch):
    cp = pytest.importorskip("cupy")

    monkeypatch.setenv("MOVIEPY_GPU_RENDER", "1")
    monkeypatch.setenv("MOVIEPY_GPU_AGGRESSIVE", "1")
    monkeypatch.setenv("MOVIEPY_GPU_RENDER_STRICT", "1")

    from moviepy.video.VideoClip import ColorClip
    from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
    from moviepy.video.tools import gpu_render

    if not gpu_render.is_available():
        pytest.skip("CuPy installed but CUDA runtime not usable")

    base = ColorClip((64, 48), color=(10, 20, 30)).with_duration(1).with_fps(5)

    inner_base = ColorClip((64, 48), color=(0, 0, 0)).with_duration(1).with_fps(5)
    inner_top = (
        ColorClip((16, 12), color=(200, 0, 0)).with_duration(1).with_fps(5).with_position((8, 9))
    )
    inner = CompositeVideoClip([inner_base, inner_top], size=(64, 48), bg_color=(0, 0, 0))

    # Without nested-composite support, the GPU compositor would fall back to
    # calling inner.get_frame() (CPU) and this would raise.
    inner.get_frame = lambda _t: (_ for _ in ()).throw(
        RuntimeError("inner get_frame should not be called in GPU path")
    )

    outer = CompositeVideoClip(
        [base, inner.with_position((0, 0))], size=(64, 48), bg_color=(0, 0, 0)
    )

    frame_gpu = gpu_render.get_frame_for_export_uint8_gpu(outer, 0)
    assert hasattr(frame_gpu, "__cuda_array_interface__")

    frame = cp.asnumpy(frame_gpu)
    assert frame.dtype == np.uint8
    assert frame.shape == (48, 64, 3)


def test_gpu_render_imageclip_cupy_img_is_cached(monkeypatch):
    cp = pytest.importorskip("cupy")

    monkeypatch.setenv("MOVIEPY_GPU_RENDER", "1")
    monkeypatch.setenv("MOVIEPY_GPU_AGGRESSIVE", "1")
    monkeypatch.setenv("MOVIEPY_GPU_RENDER_STRICT", "1")

    from moviepy.video.VideoClip import ImageClip
    from moviepy.video.tools import gpu_render

    if not gpu_render.is_available():
        pytest.skip("CuPy installed but CUDA runtime not usable")

    img_np = np.zeros((12, 16, 3), dtype=np.uint8)
    img_np[:, :, 0] = 123
    clip = ImageClip(img_np, transparent=False).with_duration(1).with_fps(5)
    # Simulate a CuPy-backed ImageClip (constructor expects NumPy/URI).
    clip.img = cp.asarray(clip.img)

    frame_gpu = gpu_render.get_frame_for_export_uint8_gpu(clip, 0)
    assert hasattr(frame_gpu, "__cuda_array_interface__")
    frame = cp.asnumpy(frame_gpu)
    assert frame.shape == (12, 16, 3)
    assert frame.dtype == np.uint8
    assert frame[0, 0].tolist() == [123, 0, 0]


def test_save_frame_accepts_cupy_frame(monkeypatch, tmp_path):
    cp = pytest.importorskip("cupy")

    from moviepy.video.VideoClip import VideoClip
    from moviepy.video.tools import gpu_render

    if not gpu_render.is_available():
        pytest.skip("CuPy installed but CUDA runtime not usable")

    def frame_function(_t):
        frame = cp.zeros((12, 16, 3), dtype=cp.uint8)
        frame[:, :, 1] = 200
        return frame

    clip = VideoClip(frame_function=frame_function, duration=1).with_fps(5)
    out = tmp_path / "cupy_save_frame.png"
    clip.save_frame(str(out), t=0)
    assert out.exists()


def test_write_images_sequence_accepts_cupy_frame(monkeypatch, tmp_path):
    cp = pytest.importorskip("cupy")

    from moviepy.video.VideoClip import VideoClip
    from moviepy.video.tools import gpu_render

    if not gpu_render.is_available():
        pytest.skip("CuPy installed but CUDA runtime not usable")

    def frame_function(_t):
        frame = cp.zeros((12, 16, 3), dtype=cp.uint8)
        frame[:, :, 2] = 255
        return frame

    clip = VideoClip(frame_function=frame_function, duration=0.41).with_fps(5)
    fmt = str(tmp_path / "frame%03d.png")

    names = clip.write_images_sequence(fmt, fps=5, with_mask=False, logger=None)
    assert len(names) >= 2
    assert (tmp_path / "frame000.png").exists()


def test_iter_frames_yields_numpy_when_frame_is_cupy(monkeypatch):
    cp = pytest.importorskip("cupy")

    from moviepy.video.VideoClip import VideoClip
    from moviepy.video.tools import gpu_render

    if not gpu_render.is_available():
        pytest.skip("CuPy installed but CUDA runtime not usable")

    def frame_function(_t):
        return cp.zeros((6, 8, 3), dtype=cp.uint8)

    clip = VideoClip(frame_function=frame_function, duration=0.41).with_fps(5)
    frames = list(clip.iter_frames(fps=5, dtype="uint8", logger=None))
    assert frames
    assert isinstance(frames[0], np.ndarray)
    assert frames[0].dtype == np.uint8


def test_write_gif_accepts_cupy_frames(monkeypatch, tmp_path):
    cp = pytest.importorskip("cupy")

    monkeypatch.setenv("MOVIEPY_GPU_RENDER", "1")
    monkeypatch.setenv("MOVIEPY_GPU_AGGRESSIVE", "1")

    from moviepy.video.VideoClip import VideoClip
    from moviepy.video.tools import gpu_render

    if not gpu_render.is_available():
        pytest.skip("CuPy installed but CUDA runtime not usable")

    def frame_function(_t):
        frame = cp.zeros((12, 16, 3), dtype=cp.uint8)
        frame[:, :, 0] = 255
        return frame

    clip = VideoClip(frame_function=frame_function, duration=0.41).with_fps(5)
    out = tmp_path / "cupy.gif"
    clip.write_gif(str(out), fps=5, loop=0, logger=None)
    assert out.exists()
