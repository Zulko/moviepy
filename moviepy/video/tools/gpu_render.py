"""Experimental GPU render path.

Goal: keep intermediate compositing math on the GPU (CuPy) during export,
and only download once per output frame for feeding FFmpeg.

This does NOT change MoviePy's public API by default.
It is used opportunistically by ffmpeg_write_video when enabled.
"""

from __future__ import annotations

import os
from typing import Tuple
import weakref

import numpy as np

from moviepy.tools import compute_position
from moviepy.video.tools import cupy_utils


def _env_flag(name: str, default: str = "0") -> bool:
    val = os.environ.get(name, default)
    return str(val).strip().lower() not in {"0", "false", "no", "off", ""}


def _strict() -> bool:
    return _env_flag("MOVIEPY_GPU_RENDER_STRICT", "0")


def is_available() -> bool:
    if _env_flag("MOVIEPY_DISABLE_GPU", "0"):
        return False
    return cupy_utils.is_cupy_usable()


def is_enabled() -> bool:
    """Whether the experimental GPU export path should be attempted.

    Default: enabled (auto) when available.
    Opt-out: set MOVIEPY_GPU_RENDER=0 or MOVIEPY_DISABLE_GPU=1.
    """
    if _env_flag("MOVIEPY_DISABLE_GPU", "0"):
        return False

    # Aggressive implies enabled.
    if _env_flag("MOVIEPY_GPU_AGGRESSIVE", "0"):
        return True

    # If user explicitly sets the flag, honor it.
    if "MOVIEPY_GPU_RENDER" in os.environ:
        return _env_flag("MOVIEPY_GPU_RENDER", "0")

    # Auto by default.
    return True


def _is_gpu_array(x) -> bool:
    return cupy_utils.is_cuda_array(x)


_IMAGE_U8_CACHE: dict[int, tuple[weakref.ref, object]] = {}
_MASK_F32_CACHE: dict[int, tuple[weakref.ref, object]] = {}


def _get_frame_gpu_best_effort(clip, t):
    """Return a CuPy array for clip.get_frame(t), best-effort.

    Prefers the internal `_gpu_frame_function` attribute (if present), which
    can keep effect chains on the GPU. Falls back to CPU get_frame upload.
    """
    cp = cupy_utils.cupy()

    gpu_fn = getattr(clip, "_gpu_frame_function", None)
    if gpu_fn is not None:
        try:
            out = gpu_fn(t)
            return out if _is_gpu_array(out) else cp.asarray(out)
        except Exception:
            if _strict():
                raise

    out = clip.get_frame(t)
    return out if _is_gpu_array(out) else cp.asarray(out)


def _get_mask_frame_gpu_best_effort(mask_clip, t):
    """Return a CuPy 2D mask frame, preserving dtype when possible."""
    cp = cupy_utils.cupy()
    m = _get_frame_gpu_best_effort(mask_clip, t)
    m = m if _is_gpu_array(m) else cp.asarray(m)
    if m.ndim == 3:
        m = m[:, :, 0]
    return m


def _cache_get(cache: dict[int, tuple[weakref.ref, object]], clip) -> object | None:
    key = id(clip)
    entry = cache.get(key)
    if entry is None:
        return None
    clip_ref, value = entry
    if clip_ref() is clip:
        return value
    # Stale id reused; drop.
    try:
        del cache[key]
    except Exception:
        pass
    return None


def _cache_set(
    cache: dict[int, tuple[weakref.ref, object]],
    clip,
    value: object,
) -> None:
    key = id(clip)

    def _cleanup(_ref, _key=key, _cache=cache):
        try:
            _cache.pop(_key, None)
        except Exception:
            pass

    cache[key] = (weakref.ref(clip, _cleanup), value)


def _cached_cp_u8_rgb_for_imageclip(clip):
    cp = cupy_utils.cupy()
    cached = _cache_get(_IMAGE_U8_CACHE, clip)
    if cached is not None:
        return cached
    arr = clip.img

    if _is_gpu_array(arr):
        a = arr
        if a.ndim == 2:
            a = cp.stack([a, a, a], axis=2)
        if a.ndim == 3 and a.shape[2] >= 3:
            a = a[:, :, :3]
        if a.dtype != cp.uint8:
            a = a.astype(cp.uint8)
        try:
            if not a.flags.c_contiguous:
                a = cp.ascontiguousarray(a)
        except Exception:
            # Best-effort; if flags isn't available, just proceed.
            pass
        _cache_set(_IMAGE_U8_CACHE, clip, a)
        return a

    # Ensure we only cache immutable-by-convention ImageClip/ColorClip backing arrays.
    if arr.dtype != np.uint8:
        arr = arr.astype(np.uint8)
    if arr.ndim == 2:
        arr = np.dstack([arr, arr, arr])
    if arr.ndim == 3 and arr.shape[2] >= 3:
        arr = arr[:, :, :3]
    if not arr.flags["C_CONTIGUOUS"]:
        arr = np.ascontiguousarray(arr)
    cached_arr = cp.asarray(arr)
    _cache_set(_IMAGE_U8_CACHE, clip, cached_arr)
    return cached_arr


def _cached_cp_f32_mask_for_imageclip(clip):
    cp = cupy_utils.cupy()
    cached = _cache_get(_MASK_F32_CACHE, clip)
    if cached is not None:
        return cached
    arr = clip.img

    if _is_gpu_array(arr):
        a = arr
        if a.ndim == 3:
            a = a[:, :, 0]
        if a.dtype != cp.float32:
            a = a.astype(cp.float32)
        try:
            if not a.flags.c_contiguous:
                a = cp.ascontiguousarray(a)
        except Exception:
            pass
        _cache_set(_MASK_F32_CACHE, clip, a)
        return a

    if isinstance(arr, np.ndarray) and arr.ndim == 3:
        arr = arr[:, :, 0]
    if not isinstance(arr, np.ndarray):
        arr = np.asarray(arr)
    if arr.dtype != np.float32:
        arr = arr.astype(np.float32)
    if not arr.flags["C_CONTIGUOUS"]:
        arr = np.ascontiguousarray(arr)
    cached_arr = cp.asarray(arr)
    _cache_set(_MASK_F32_CACHE, clip, cached_arr)
    return cached_arr


def _to_cp_u8_rgb(frame):
    cp = cupy_utils.cupy()
    f = frame if _is_gpu_array(frame) else cp.asarray(frame)
    if f.ndim == 2:
        f = cp.stack([f, f, f], axis=2)
    if f.ndim == 3 and f.shape[2] >= 3:
        f = f[:, :, :3]
    if f.dtype != cp.uint8:
        f = f.astype(cp.uint8)
    return f


def _to_cp_f32_mask(mask):
    cp = cupy_utils.cupy()
    m = mask if _is_gpu_array(mask) else cp.asarray(mask)
    if m.ndim == 3:
        m = m[:, :, 0]
    if m.dtype != cp.float32:
        m = m.astype(cp.float32)
    return m


def _to_cp_mask(mask, dtype):
    cp = cupy_utils.cupy()
    m = mask if _is_gpu_array(mask) else cp.asarray(mask)
    if m.ndim == 3:
        m = m[:, :, 0]
    if m.dtype != dtype:
        m = m.astype(dtype)
    return m


def _as_u8_rgb(frame: np.ndarray) -> np.ndarray:
    if frame.ndim == 2:
        frame = np.dstack([frame, frame, frame])
    if frame.ndim == 3 and frame.shape[2] >= 3:
        frame = frame[:, :, :3]
    if frame.dtype != np.uint8:
        frame = frame.astype(np.uint8)
    return frame


def _as_f32_mask(mask: np.ndarray) -> np.ndarray:
    if mask.ndim == 3:
        mask = mask[:, :, 0]
    if mask.dtype != np.float32:
        mask = mask.astype(np.float32)
    return mask


def _coords_for_layer(
    background_size: Tuple[int, int],
    clip_size: Tuple[int, int],
    x_start: int,
    y_start: int,
):
    background_width, background_height = background_size
    clip_width, clip_height = clip_size

    y1_bg = max(y_start, 0)
    y2_bg = min(y_start + clip_height, background_height)
    x1_bg = max(x_start, 0)
    x2_bg = min(x_start + clip_width, background_width)

    y1_clip = max(-y_start, 0)
    y2_clip = y1_clip + (y2_bg - y1_bg)
    x1_clip = max(-x_start, 0)
    x2_clip = x1_clip + (x2_bg - x1_bg)

    return y1_bg, y2_bg, x1_bg, x2_bg, y1_clip, y2_clip, x1_clip, x2_clip


def _composite_rgb_gpu(clip, t):
    """Return a CuPy uint8 RGB frame for a (possibly composite) clip."""
    cp = cupy_utils.cupy()

    # CompositeVideoClip path
    from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
    from moviepy.video.VideoClip import ImageClip, ColorClip

    if isinstance(clip, CompositeVideoClip):
        playing = clip.playing_clips(t)

        # Fast-path: if no playing layer has a mask, we can composite entirely
        # in uint8 (no alpha blending), avoiding a full-frame float32 buffer.
        any_layer_has_mask = any(
            getattr(layer, "mask", None) is not None for layer in playing
        )

        bg_t = t - clip.bg.start
        if isinstance(clip.bg, CompositeVideoClip):
            bg_u8 = _composite_rgb_gpu(clip.bg, bg_t)
        elif isinstance(clip.bg, (ImageClip, ColorClip)) and hasattr(clip.bg, "img"):
            bg_u8 = _cached_cp_u8_rgb_for_imageclip(clip.bg)
        else:
            bg_u8 = _to_cp_u8_rgb(_get_frame_gpu_best_effort(clip.bg, bg_t))

        bg_f = None

        bg_mask_f = None
        if clip.bg.mask and any_layer_has_mask:
            bgm_t = t - clip.bg.mask.start
            if isinstance(clip.bg.mask, (ImageClip, ColorClip)) and getattr(
                clip.bg.mask, "is_mask", False
            ) and hasattr(clip.bg.mask, "img"):
                bg_mask_f = _cached_cp_f32_mask_for_imageclip(clip.bg.mask)
            else:
                bg_mask_f = _composite_mask_gpu(clip.bg.mask, bgm_t, dtype=cp.float32)

        bg_h, bg_w = int(bg_u8.shape[0]), int(bg_u8.shape[1])

        for layer in playing:
            ct = t - layer.start
            if isinstance(layer, CompositeVideoClip):
                fr_u8 = _composite_rgb_gpu(layer, ct)
            elif isinstance(layer, (ImageClip, ColorClip)) and hasattr(layer, "img"):
                fr_u8 = _cached_cp_u8_rgb_for_imageclip(layer)
            else:
                fr_u8 = _to_cp_u8_rgb(_get_frame_gpu_best_effort(layer, ct))

            layer_mask = None
            if layer.mask is not None:
                if isinstance(layer.mask, (ImageClip, ColorClip)) and getattr(
                    layer.mask, "is_mask", False
                ) and hasattr(layer.mask, "img"):
                    layer_mask = _cached_cp_f32_mask_for_imageclip(layer.mask)
                elif isinstance(layer.mask, CompositeVideoClip) and getattr(
                    layer.mask,
                    "is_mask",
                    False,
                ):
                    layer_mask = _composite_mask_gpu(layer.mask, ct, dtype=cp.float32)
                else:
                    layer_mask = _get_mask_frame_gpu_best_effort(layer.mask, ct)

            pos = layer.pos(ct)
            x_start, y_start = compute_position(
                (int(fr_u8.shape[1]), int(fr_u8.shape[0])),
                (bg_w, bg_h),
                pos,
                layer.relative_pos,
            )

            (
                y1_bg,
                y2_bg,
                x1_bg,
                x2_bg,
                y1_clip,
                y2_clip,
                x1_clip,
                x2_clip,
            ) = _coords_for_layer(
                (bg_w, bg_h),
                (int(fr_u8.shape[1]), int(fr_u8.shape[0])),
                x_start,
                y_start,
            )

            if (y2_bg <= y1_bg) or (x2_bg <= x1_bg):
                continue
            fr_u8_region = fr_u8[y1_clip:y2_clip, x1_clip:x2_clip]

            if layer_mask is None:
                if bg_f is None:
                    bg_u8[y1_bg:y2_bg, x1_bg:x2_bg] = fr_u8_region
                else:
                    bg_region = bg_f[y1_bg:y2_bg, x1_bg:x2_bg]
                    bg_region[...] = fr_u8_region
                if bg_mask_f is not None:
                    bg_mask_f[y1_bg:y2_bg, x1_bg:x2_bg] = 1.0
                continue

            # First masked layer triggers float32 compositing.
            if bg_f is None:
                bg_f = bg_u8.astype(cp.float32)

            bg_region = bg_f[y1_bg:y2_bg, x1_bg:x2_bg]

            a = layer_mask[y1_clip:y2_clip, x1_clip:x2_clip]
            if a.dtype != cp.float32:
                a = a.astype(cp.float32)
            fr_region = fr_u8_region.astype(cp.float32)

            if bg_mask_f is None:
                # bg = bg + a*(fr - bg)
                cp.subtract(fr_region, bg_region, out=fr_region)
                fr_region *= a[:, :, None]
                bg_region += fr_region
            else:
                # final_a = a + bg_a*(1-a)
                bg_a = bg_mask_f[y1_bg:y2_bg, x1_bg:x2_bg]
                one_minus_a = 1.0 - a
                final_a = a + bg_a * one_minus_a
                safe_a = cp.where(final_a == 0, 1.0, final_a)

                # numerator = fr*a + bg*bg_a*(1-a)
                # reuse fr_region as temp: fr*a
                fr_region *= a[:, :, None]
                bg_region *= (bg_a * one_minus_a)[:, :, None]
                bg_region += fr_region
                bg_region /= safe_a[:, :, None]

                bg_a[...] = final_a

        if bg_f is None:
            return bg_u8

        cp.rint(bg_f, out=bg_f)
        cp.clip(bg_f, 0, 255, out=bg_f)
        return bg_f.astype(cp.uint8)

    # Non-composite: keep static ImageClips on GPU without re-upload.
    if isinstance(clip, (ImageClip, ColorClip)) and hasattr(clip, "img"):
        return _cached_cp_u8_rgb_for_imageclip(clip)
    return _to_cp_u8_rgb(_get_frame_gpu_best_effort(clip, t))


def _composite_mask_gpu(mask_clip, t, *, dtype=None):
    """Return a CuPy floating mask frame.

    For parity with CPU semantics:
    - CompositeVideoClip masks are computed in float64 on CPU, so callers that
      care about exact export rounding should request float64.
    - Alpha blending inside RGB compositing uses float32 on CPU.
    """
    cp = cupy_utils.cupy()
    if dtype is None:
        dtype = cp.float32

    from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
    from moviepy.video.VideoClip import ImageClip, ColorClip

    if isinstance(mask_clip, CompositeVideoClip) and mask_clip.is_mask:
        h, w = mask_clip.size[1], mask_clip.size[0]
        b = cp.zeros((h, w), dtype=dtype)

        for layer in mask_clip.playing_clips(t):
            ct = t - layer.start
            if isinstance(layer, CompositeVideoClip) and getattr(
                layer,
                "is_mask",
                False,
            ):
                m = _composite_mask_gpu(layer, ct, dtype=dtype)
            else:
                m = _get_frame_gpu_best_effort(layer, ct)
                m = m if _is_gpu_array(m) else cp.asarray(m)
                if m.ndim == 3:
                    m = m[:, :, 0]

            pos = layer.pos(ct)
            x_start, y_start = compute_position(
                (int(m.shape[1]), int(m.shape[0])),
                (w, h),
                pos,
                layer.relative_pos,
            )

            (
                y1_bg,
                y2_bg,
                x1_bg,
                x2_bg,
                y1_clip,
                y2_clip,
                x1_clip,
                x2_clip,
            ) = _coords_for_layer(
                (w, h), (int(m.shape[1]), int(m.shape[0])), x_start, y_start
            )

            if (y2_bg <= y1_bg) or (x2_bg <= x1_bg):
                continue

            b_region = b[y1_bg:y2_bg, x1_bg:x2_bg]
            m_region = m[y1_clip:y2_clip, x1_clip:x2_clip]
            if m_region.dtype != dtype:
                m_region = m_region.astype(dtype)

            # b = m + b*(1-m)
            b_region *= (1.0 - m_region)
            b_region += m_region

        return b

    if (
        isinstance(mask_clip, (ImageClip, ColorClip))
        and getattr(mask_clip, "is_mask", False)
        and hasattr(mask_clip, "img")
    ):
        m = _cached_cp_f32_mask_for_imageclip(mask_clip)
        if dtype != cp.float32:
            m = m.astype(dtype)
        return m

    return _to_cp_mask(_get_frame_gpu_best_effort(mask_clip, t), dtype)


def get_frame_for_export_uint8(clip, t: float):
    """Return a NumPy uint8 frame ready for ffmpeg_writer.

    If clip has a mask, returns RGBA uint8; otherwise RGB uint8.

    Falls back to CPU path on any error.
    """
    if not (is_enabled() and is_available()):
        frame = clip.get_frame(t)
        if frame.dtype != np.uint8:
            frame = frame.astype(np.uint8)
        return frame

    cp = cupy_utils.cupy()

    try:
        rgb_u8 = _composite_rgb_gpu(clip, t)
        if clip.mask is None:
            return cp.asnumpy(rgb_u8)

        # Match CPU export path semantics exactly:
        # mask_u8 = (255 * mask_frame).astype(uint8) with NumPy/CuPy overflow
        # behavior for uint8 masks, and stack via dstack semantics.
        from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

        if isinstance(clip.mask, CompositeVideoClip) and getattr(
            clip.mask,
            "is_mask",
            False,
        ):
            m = _composite_mask_gpu(clip.mask, t, dtype=cp.float64)
        else:
            m = _get_frame_gpu_best_effort(clip.mask, t)
            m = m if _is_gpu_array(m) else cp.asarray(m)
        m_u8 = m * 255
        if m_u8.dtype != cp.uint8:
            m_u8 = m_u8.astype(cp.uint8)
        if m_u8.ndim == 2:
            m_u8 = m_u8[:, :, None]
        rgba = cp.concatenate([rgb_u8, m_u8], axis=2)
        return cp.asnumpy(rgba)
    except Exception:
        if _strict():
            raise
        # Best-effort: never fail export.
        frame = clip.get_frame(t)
        if frame.dtype != np.uint8:
            frame = frame.astype(np.uint8)
        if clip.mask is not None:
            mask = 255 * clip.mask.get_frame(t)
            if mask.dtype != np.uint8:
                mask = mask.astype(np.uint8)
            frame = np.dstack([frame, mask])
        return frame


def get_frame_for_export_uint8_gpu(clip, t: float):
    """Return a CuPy uint8 frame (RGB or RGBA) for ffmpeg export.

    This is the "CuPy-native" experimental export pipeline: all compositing
    work happens on the GPU and the returned frame is a CuPy array. The only
    CPU conversion happens at the final FFmpeg write.

    On any error, returns a NumPy uint8 frame as a safe fallback.
    """
    if not (is_enabled() and is_available()):
        frame = clip.get_frame(t)
        if frame.dtype != np.uint8:
            frame = frame.astype(np.uint8)
        if clip.mask is not None:
            mask = 255 * clip.mask.get_frame(t)
            if mask.dtype != np.uint8:
                mask = mask.astype(np.uint8)
            frame = np.dstack([frame, mask])
        return frame

    cp = cupy_utils.cupy()
    try:
        rgb_u8 = _composite_rgb_gpu(clip, t)
        if clip.mask is None:
            return rgb_u8

        # Match CPU export path semantics exactly:
        # mask_u8 = (255 * mask_frame).astype(uint8) with CuPy overflow
        # behavior for uint8 masks, and stack via dstack semantics.
        from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

        if isinstance(clip.mask, CompositeVideoClip) and getattr(
            clip.mask,
            "is_mask",
            False,
        ):
            m = _composite_mask_gpu(clip.mask, t, dtype=cp.float64)
        else:
            m = _get_frame_gpu_best_effort(clip.mask, t)
            m = m if _is_gpu_array(m) else cp.asarray(m)
        m_u8 = m * 255
        if m_u8.dtype != cp.uint8:
            m_u8 = m_u8.astype(cp.uint8)
        if m_u8.ndim == 2:
            m_u8 = m_u8[:, :, None]
        rgba = cp.concatenate([rgb_u8, m_u8], axis=2)
        return rgba
    except Exception:
        if _strict():
            raise
        frame = clip.get_frame(t)
        if frame.dtype != np.uint8:
            frame = frame.astype(np.uint8)
        if clip.mask is not None:
            mask = 255 * clip.mask.get_frame(t)
            if mask.dtype != np.uint8:
                mask = mask.astype(np.uint8)
            frame = np.dstack([frame, mask])
        return frame
