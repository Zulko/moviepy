from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from moviepy.Clip import Clip
from moviepy.Effect import Effect
from moviepy.video.tools import cupy_utils


@dataclass
class GPUConvertToNV12(Effect):
    """Internal helper effect: convert frames to NV12 on GPU.

    This effect is intentionally *GPU-only*: it does not change the CPU
    `frame_function` output (still RGB). Instead it installs/overrides the
    internal `_gpu_frame_function` so GPU export/encode pipelines can consume
    NV12 directly.

    Color settings default to env/config used by the NVENC pipeline.

    Notes
    -----
    - Not exported via `moviepy.video.fx` public namespace.
    - Intended for internal/advanced usage.
    """

    color_matrix: Optional[str] = None  # "bt601" or "bt709"
    color_range: Optional[str] = None  # "mpeg" (limited) or "jpeg" (full)

    def apply(self, clip: Clip) -> Clip:
        new_clip = clip.copy()

        # Import conversion helpers from NVENC writer module to avoid duplicating
        # kernel code. This module is internal and best-effort.
        from moviepy.video.io import pynvcodec_writer as _nv

        matrix, crange = _nv._gpu_color_settings_for_clip(clip)
        if self.color_matrix is not None:
            matrix = _nv._parse_color_matrix(self.color_matrix)
        if self.color_range is not None:
            crange = _nv._parse_color_range(self.color_range)

        new_clip._gpu_frame_format = "nv12"
        new_clip._gpu_color_matrix = matrix
        new_clip._gpu_color_range = crange

        def _gpu_frame_function(t):
            cp = cupy_utils.cupy()

            # If upstream already provides NV12, pass through.
            src_gpu_fn = getattr(clip, "_gpu_frame_function", None)
            if src_gpu_fn is not None:
                try:
                    v = src_gpu_fn(t)
                    if callable(getattr(v, "cuda", None)):
                        return v
                    if cupy_utils.is_cuda_array(v):
                        # packed NV12 (H+H/2,W) or planes are accepted downstream
                        if v.ndim == 2 and v.dtype == cp.uint8:
                            return v
                    if isinstance(v, (tuple, list)) and len(v) == 2 and all(
                        cupy_utils.is_cuda_array(p) for p in v
                    ):
                        return v
                except Exception:
                    pass

            # Get an RGB frame, best-effort on GPU.
            if src_gpu_fn is not None:
                try:
                    frame = src_gpu_fn(t)
                except Exception:
                    frame = clip.get_frame(t)
            else:
                frame = clip.get_frame(t)

            if not cupy_utils.is_cuda_array(frame):
                if not isinstance(frame, np.ndarray):
                    frame = np.asarray(frame)
                frame = cp.asarray(frame)

            if frame.ndim != 3 or frame.shape[2] < 3:
                raise ValueError(
                    "Expected HxWx3(+) RGB frame for NV12 conversion, got "
                    f"shape={getattr(frame, 'shape', None)!r}"
                )

            frame = frame[:, :, :3]
            if frame.dtype != cp.uint8:
                frame = frame.astype(cp.uint8)
            try:
                if not frame.flags.c_contiguous:
                    frame = cp.ascontiguousarray(frame)
            except Exception:
                frame = cp.ascontiguousarray(frame)

            h = int(frame.shape[0])
            w = int(frame.shape[1])
            if (w % 2) or (h % 2):
                raise ValueError("NV12 requires even frame dimensions")

            nv12 = cp.empty((h + h // 2, w), dtype=cp.uint8)
            y = nv12[:h, :]
            uv = nv12[h : h + h // 2, :]

            kernel = _nv._get_rgb_to_nv12_kernel(cp, matrix=matrix, crange=crange)

            threads = (16, 16)
            grid = (
                ((w // 2) + threads[0] - 1) // threads[0],
                ((h // 2) + threads[1] - 1) // threads[1],
            )
            kernel(
                grid,
                threads,
                (
                    frame,
                    y,
                    uv,
                    int(w),
                    int(h),
                    int(frame.strides[0]),
                    int(y.strides[0]),
                    int(uv.strides[0]),
                ),
            )

            return nv12

        new_clip._gpu_frame_function = _gpu_frame_function
        return new_clip
