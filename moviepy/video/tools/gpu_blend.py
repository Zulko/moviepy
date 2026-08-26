"""Optional GPU blending helpers (internal).

These helpers are best-effort and must never change MoviePy public APIs.
They attempt to use CuPy (CUDA) when available and fall back silently to
CPU paths on any error or OOM.

We intentionally operate on *regions* and copy results back to NumPy arrays.
Keeping whole-frame state on the GPU would require broader architectural changes.
"""

from __future__ import annotations

import os
from typing import Any

from moviepy.video.tools import cupy_utils


def _env_flag(name: str, default: str = "0") -> bool:
    val = os.environ.get(name, default)
    return str(val).strip().lower() not in {"0", "false", "no", "off", ""}


def is_available() -> bool:
    if _env_flag("MOVIEPY_DISABLE_GPU", "0"):
        return False
    if _has_cupy():
        return True
    if _has_opencv_cuda():
        return True
    return False


def _has_cupy() -> bool:
    return cupy_utils.is_cupy_usable()


def _has_opencv_cuda() -> bool:
    try:
        import cv2

        if not hasattr(cv2, "cuda"):
            return False
        if not hasattr(cv2.cuda, "getCudaEnabledDeviceCount"):
            return False
        return int(cv2.cuda.getCudaEnabledDeviceCount()) > 0
    except Exception:
        return False


def _min_pixels() -> int:
    # Heuristic gate to avoid GPU upload/download overhead on small regions.
    # Set MOVIEPY_GPU_AGGRESSIVE=1 to default to always-on.
    if _env_flag("MOVIEPY_GPU_AGGRESSIVE", "0"):
        return 0

    # Default to always-on when a GPU backend is present.
    val = os.environ.get("MOVIEPY_GPU_MIN_PIXELS", "0")
    try:
        return max(0, int(val))
    except Exception:
        return 0


def should_use_gpu(h: int, w: int) -> bool:
    return (h * w) >= _min_pixels()


def _cp() -> Any:
    return cupy_utils.cupy()


def _try_run_opencv_cuda(fn):
    def _wrapped(*args, **kwargs) -> bool:
        try:
            import cv2

            return bool(fn(cv2, *args, **kwargs))
        except Exception:
            return False

    return _wrapped


def _has_enough_vram(cp: Any, bytes_needed: int) -> bool:
    try:
        free_bytes, total_bytes = cp.cuda.runtime.memGetInfo()
    except Exception:
        return True

    # Be conservative: require a safety margin.
    # In aggressive mode, use a smaller margin and rely on OOM fallback.
    margin = 1.1 if _env_flag("MOVIEPY_GPU_AGGRESSIVE", "0") else 1.5
    return free_bytes > int(bytes_needed * margin)


def _on_oom(cp: Any) -> None:
    try:
        cp.get_default_memory_pool().free_all_blocks()
    except Exception:
        pass


def _try_run(fn):
    """Decorator-like helper to convert GPU errors into a boolean result."""

    def _wrapped(*args, **kwargs) -> bool:
        cp = _cp()
        try:
            return bool(fn(cp, *args, **kwargs))
        except Exception as exc:
            # CuPy raises different errors depending on version/driver.
            oom_types = []
            try:
                oom_types.append(cp.cuda.memory.OutOfMemoryError)
            except Exception:
                pass

            if any(isinstance(exc, t) for t in oom_types):
                _on_oom(cp)
                return False

            # Generic runtime / driver errors: fall back.
            return False

    return _wrapped


def blend_over_opaque_u8(
    bg_copy,
    clip_frame,
    alpha2d,
    y1_bg: int,
    y2_bg: int,
    x1_bg: int,
    x2_bg: int,
    y1_clip: int,
    y2_clip: int,
    x1_clip: int,
    x2_clip: int,
) -> bool:
    """Dispatch to the best available GPU backend.

    Preference order: CuPy (CUDA) > OpenCV CUDA.
    """
    if _has_cupy():
        return _blend_over_opaque_u8_cupy(
            bg_copy,
            clip_frame,
            alpha2d,
            y1_bg,
            y2_bg,
            x1_bg,
            x2_bg,
            y1_clip,
            y2_clip,
            x1_clip,
            x2_clip,
        )
    if _has_opencv_cuda():
        return _blend_over_opaque_u8_opencv_cuda(
            bg_copy,
            clip_frame,
            alpha2d,
            y1_bg,
            y2_bg,
            x1_bg,
            x2_bg,
            y1_clip,
            y2_clip,
            x1_clip,
            x2_clip,
        )
    return False


@_try_run
def _blend_over_opaque_u8_cupy(
    cp: Any,
    bg_copy,
    clip_frame,
    alpha2d,
    y1_bg: int,
    y2_bg: int,
    x1_bg: int,
    x2_bg: int,
    y1_clip: int,
    y2_clip: int,
    x1_clip: int,
    x2_clip: int,
) -> bool:
    """Blend clip over an opaque background (uint8 RGB), in-place into bg_copy.

    Returns True if GPU path succeeded.
    """
    bg_region = bg_copy[y1_bg:y2_bg, x1_bg:x2_bg]
    fr_region = clip_frame[y1_clip:y2_clip, x1_clip:x2_clip]
    a_region = alpha2d[y1_clip:y2_clip, x1_clip:x2_clip]

    h, w = bg_region.shape[:2]
    if h <= 0 or w <= 0:
        return True

    # Rough VRAM estimate: two float32 RGB + one float32 alpha.
    bytes_needed = h * w * (3 * 4 * 2 + 4)
    if not _has_enough_vram(cp, bytes_needed):
        return False

    bg = cp.asarray(bg_region, dtype=cp.float32)
    fr = cp.asarray(fr_region, dtype=cp.float32)
    a = cp.asarray(a_region, dtype=cp.float32)

    # result = bg + a * (fr - bg) (minimize temporaries)
    cp.subtract(fr, bg, out=fr)
    fr *= a[:, :, None]
    fr += bg
    cp.rint(fr, out=fr)
    cp.clip(fr, 0, 255, out=fr)
    out_u8 = fr.astype(cp.uint8)

    bg_region[...] = cp.asnumpy(out_u8)
    return True


@_try_run_opencv_cuda
def _blend_over_opaque_u8_opencv_cuda(
    cv2: Any,
    bg_copy,
    clip_frame,
    alpha2d,
    y1_bg: int,
    y2_bg: int,
    x1_bg: int,
    x2_bg: int,
    y1_clip: int,
    y2_clip: int,
    x1_clip: int,
    x2_clip: int,
) -> bool:
    # Keep this conservative: compute on GPU, but do rounding/clipping on CPU
    # to better match NumPy semantics.
    bg_region = bg_copy[y1_bg:y2_bg, x1_bg:x2_bg]
    fr_region = clip_frame[y1_clip:y2_clip, x1_clip:x2_clip]
    a_region = alpha2d[y1_clip:y2_clip, x1_clip:x2_clip]

    h, w = bg_region.shape[:2]
    if h <= 0 or w <= 0:
        return True

    bg_gpu = cv2.cuda_GpuMat()
    fr_gpu = cv2.cuda_GpuMat()
    a_gpu = cv2.cuda_GpuMat()
    bg_gpu.upload(bg_region)
    fr_gpu.upload(fr_region)
    a_gpu.upload(a_region)

    bg_f = bg_gpu.convertTo(cv2.CV_32F)
    fr_f = fr_gpu.convertTo(cv2.CV_32F)
    a_f = a_gpu.convertTo(cv2.CV_32F)

    # Expand alpha to 3 channels.
    a3 = cv2.cuda.merge([a_f, a_f, a_f])

    diff = cv2.cuda.subtract(fr_f, bg_f)
    diff = cv2.cuda.multiply(diff, a3)
    out_f = cv2.cuda.add(bg_f, diff)

    out = out_f.download()
    # CPU rounding/clipping for stable semantics.
    import numpy as np

    np.rint(out, out=out)
    out = np.clip(out, 0, 255).astype(np.uint8)
    bg_region[...] = out
    return True


def blend_over_with_masks_u8(
    bg_copy,
    bg_mask_copy,
    clip_frame,
    alpha2d,
    y1_bg: int,
    y2_bg: int,
    x1_bg: int,
    x2_bg: int,
    y1_clip: int,
    y2_clip: int,
    x1_clip: int,
    x2_clip: int,
) -> bool:
    if _has_cupy():
        return _blend_over_with_masks_u8_cupy(
            bg_copy,
            bg_mask_copy,
            clip_frame,
            alpha2d,
            y1_bg,
            y2_bg,
            x1_bg,
            x2_bg,
            y1_clip,
            y2_clip,
            x1_clip,
            x2_clip,
        )
    if _has_opencv_cuda():
        return _blend_over_with_masks_u8_opencv_cuda(
            bg_copy,
            bg_mask_copy,
            clip_frame,
            alpha2d,
            y1_bg,
            y2_bg,
            x1_bg,
            x2_bg,
            y1_clip,
            y2_clip,
            x1_clip,
            x2_clip,
        )
    return False


@_try_run
def _blend_over_with_masks_u8_cupy(
    cp: Any,
    bg_copy,
    bg_mask_copy,
    clip_frame,
    alpha2d,
    y1_bg: int,
    y2_bg: int,
    x1_bg: int,
    x2_bg: int,
    y1_clip: int,
    y2_clip: int,
    x1_clip: int,
    x2_clip: int,
) -> bool:
    """Blend clip over background where both have masks.

    Updates bg_copy (uint8 RGB) and bg_mask_copy (float mask) in-place.
    Returns True if GPU path succeeded.
    """
    bg_region = bg_copy[y1_bg:y2_bg, x1_bg:x2_bg]
    fr_region = clip_frame[y1_clip:y2_clip, x1_clip:x2_clip]
    a_clip_region = alpha2d[y1_clip:y2_clip, x1_clip:x2_clip]
    a_bg_region = bg_mask_copy[y1_bg:y2_bg, x1_bg:x2_bg]

    h, w = bg_region.shape[:2]
    if h <= 0 or w <= 0:
        return True

    # Rough VRAM estimate: two float32 RGB + three float32 masks.
    bytes_needed = h * w * (3 * 4 * 2 + 4 * 3)
    if not _has_enough_vram(cp, bytes_needed):
        return False

    bg = cp.asarray(bg_region, dtype=cp.float32)
    fr = cp.asarray(fr_region, dtype=cp.float32)
    a_clip = cp.asarray(a_clip_region, dtype=cp.float32)
    a_bg = cp.asarray(a_bg_region, dtype=cp.float32)

    # tmp = (1 - a_clip)
    tmp = 1.0 - a_clip
    final_a = a_clip + a_bg * tmp
    safe_a = cp.where(final_a == 0, 1.0, final_a)

    # fr <- fr * a_clip
    fr *= a_clip[:, :, None]

    # a_bg <- a_bg * (1 - a_clip)
    a_bg *= tmp

    # bg <- bg * a_bg
    bg *= a_bg[:, :, None]

    # fr <- fr + bg
    fr += bg

    # fr <- fr / safe_a
    fr /= safe_a[:, :, None]

    cp.rint(fr, out=fr)
    cp.clip(fr, 0, 255, out=fr)
    out_u8 = fr.astype(cp.uint8)

    bg_region[...] = cp.asnumpy(out_u8)
    bg_mask_copy[y1_bg:y2_bg, x1_bg:x2_bg] = cp.asnumpy(final_a)
    return True


@_try_run_opencv_cuda
def _blend_over_with_masks_u8_opencv_cuda(
    cv2: Any,
    bg_copy,
    bg_mask_copy,
    clip_frame,
    alpha2d,
    y1_bg: int,
    y2_bg: int,
    x1_bg: int,
    x2_bg: int,
    y1_clip: int,
    y2_clip: int,
    x1_clip: int,
    x2_clip: int,
) -> bool:
    # Conservative implementation: compute float output on GPU, round on CPU.
    import numpy as np

    bg_region = bg_copy[y1_bg:y2_bg, x1_bg:x2_bg]
    fr_region = clip_frame[y1_clip:y2_clip, x1_clip:x2_clip]
    a_clip_region = alpha2d[y1_clip:y2_clip, x1_clip:x2_clip]
    a_bg_region = bg_mask_copy[y1_bg:y2_bg, x1_bg:x2_bg]

    h, w = bg_region.shape[:2]
    if h <= 0 or w <= 0:
        return True

    bg_gpu = cv2.cuda_GpuMat()
    bg_gpu.upload(bg_region)
    fr_gpu = cv2.cuda_GpuMat()
    fr_gpu.upload(fr_region)

    a_clip_f32 = a_clip_region.astype(np.float32, copy=False)
    ac_gpu = cv2.cuda_GpuMat()
    ac_gpu.upload(a_clip_f32)

    a_bg_f32 = a_bg_region.astype(np.float32, copy=False)
    ab_gpu = cv2.cuda_GpuMat()
    ab_gpu.upload(a_bg_f32)

    bg_f = bg_gpu.convertTo(cv2.CV_32F)
    fr_f = fr_gpu.convertTo(cv2.CV_32F)
    ac_f = ac_gpu.convertTo(cv2.CV_32F)
    ab_f = ab_gpu.convertTo(cv2.CV_32F)

    one = cv2.cuda_GpuMat()
    one.upload(np.ones((h, w), dtype=np.float32))
    one_minus_ac = cv2.cuda.subtract(one, ac_f)
    final_a = cv2.cuda.add(ac_f, cv2.cuda.multiply(ab_f, one_minus_ac))

    ac3 = cv2.cuda.merge([ac_f, ac_f, ac_f])
    bw = cv2.cuda.multiply(ab_f, one_minus_ac)
    bw3 = cv2.cuda.merge([bw, bw, bw])

    num = cv2.cuda.add(cv2.cuda.multiply(fr_f, ac3), cv2.cuda.multiply(bg_f, bw3))

    # Match CPU semantics: safe_alpha = where(final_a == 0, 1.0, final_a)
    final_a_cpu = final_a.download()
    safe_a_cpu = final_a_cpu.copy()
    safe_a_cpu[safe_a_cpu == 0] = 1.0
    safe_a = cv2.cuda_GpuMat()
    safe_a.upload(safe_a_cpu)
    safe_a3 = cv2.cuda.merge([safe_a, safe_a, safe_a])

    out_f = cv2.cuda.divide(num, safe_a3)

    out = out_f.download()
    np.rint(out, out=out)
    out = np.clip(out, 0, 255).astype(np.uint8)
    bg_region[...] = out
    bg_mask_copy[y1_bg:y2_bg, x1_bg:x2_bg] = final_a_cpu
    return True
