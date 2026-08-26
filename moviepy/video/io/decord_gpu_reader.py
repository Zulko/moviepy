"""Optional GPU video reader backend using `decord`.

This reader is internal-only and is used opportunistically when the experimental
GPU render path is enabled.

If `decord` is unavailable (or cannot initialize a GPU context), callers must
fall back to the standard readers.

Design goals:
- Keep decoded frames GPU-resident (no ffmpeg stdout pipe).
- Expose a CuPy frame path via `get_frame_gpu(t)`.
- Preserve MoviePy public semantics: `get_frame(t)` returns a NumPy array.
"""

from __future__ import annotations

from typing import Any
from typing import Sequence

import numpy as np


class DecordGPUVideoReader:
    """Best-effort GPU video reader using NVDEC via decord.

    Parameters match the subset needed by `VideoFileClip`.

    Notes
    -----
    - Only supports `pixel_format="rgb24"`.
    - `get_frame(t)` downloads to NumPy for public API compatibility.
    - `get_frame_gpu(t)` returns a CuPy uint8 RGB array when possible.
    """

    def __init__(
        self,
        filename: str,
        *,
        infos: dict,
        target_resolution=None,
        pixel_format: str = "rgb24",
        resize_algo: str | None = None,
        ctx_id: int = 0,
    ):
        if str(pixel_format).lower() != "rgb24":
            raise ValueError("DecordGPUVideoReader only supports pixel_format=rgb24")

        # Import lazily to keep this backend optional.
        import decord  # type: ignore

        self.filename = filename
        self.infos = infos

        self.fps = float(infos.get("video_fps", 1.0) or 1.0)
        self.duration = float(infos.get("video_duration", 0.0) or 0.0)
        self.ffmpeg_duration = float(infos.get("duration", 0.0) or 0.0)
        self.n_frames = int(infos.get("video_n_frames", 0) or 0)
        self.bitrate = infos.get("video_bitrate", 0)

        self.rotation = abs(infos.get("video_rotation", 0) or 0)
        self.size = infos.get("video_size", (1, 1))
        if self.rotation in [90, 270]:
            self.size = [self.size[1], self.size[0]]

        self.pixel_format = pixel_format
        self.depth = 3
        self.resize_algo = resize_algo or "bicubic"

        kwargs: dict[str, Any] = {}

        # Decord supports optional decode-time resizing via (width, height).
        if target_resolution is not None:
            if None in target_resolution:
                raise ValueError(
                    "DecordGPUVideoReader requires explicit (w, h) target_resolution"
                )
            w, h = target_resolution
            if w and h:
                kwargs["width"] = int(w)
                kwargs["height"] = int(h)
                self.size = (int(w), int(h))

        self._decord = decord
        self._ctx = decord.gpu(int(ctx_id))
        self._vr = decord.VideoReader(filename, ctx=self._ctx, **kwargs)

        # Some containers report 0 frames; fall back to len(vr).
        try:
            self.n_frames = self.n_frames or int(len(self._vr))
        except Exception:
            pass

    def get_frame_number(self, t: float) -> int:
        # Match MoviePy reader rounding.
        idx = int(self.fps * t + 0.00001)
        if idx < 0:
            return 0
        if self.n_frames:
            return min(idx, self.n_frames - 1)
        return idx

    def get_frame_gpu(self, t: float):
        """Return a CuPy uint8 RGB frame (H, W, 3) on GPU."""
        from moviepy.video.tools import cupy_utils

        cp = cupy_utils.cupy()

        idx = self.get_frame_number(t)
        frame = self._vr[idx]

        # Convert decord NDArray -> CuPy via DLPack (zero-copy on GPU).
        if hasattr(frame, "to_dlpack"):
            capsule = frame.to_dlpack()
            try:
                out = cp.fromDlpack(capsule)  # CuPy < 13
            except Exception:
                out = cp.from_dlpack(capsule)  # CuPy >= 13
        else:
            # Fall back (may download to CPU inside decord).
            out = cp.asarray(frame.asnumpy())

        if out.ndim == 2:
            out = cp.stack([out, out, out], axis=2)
        if out.ndim == 3 and out.shape[2] >= 3:
            out = out[:, :, :3]
        if out.dtype != cp.uint8:
            out = out.astype(cp.uint8)

        try:
            if not out.flags.c_contiguous:
                out = cp.ascontiguousarray(out)
        except Exception:
            pass

        return out

    def get_batch_gpu(self, indices: Sequence[int]):
        """Return a batch of CuPy uint8 RGB frames (N, H, W, 3) on GPU.

        This is best-effort and relies on decord's `get_batch` for fewer
        Python/host round-trips.
        """
        if not indices:
            raise ValueError("indices must be non-empty")

        from moviepy.video.tools import cupy_utils

        cp = cupy_utils.cupy()

        # Decord expects a list-like of ints.
        idxs = [int(i) for i in indices]
        batch = self._vr.get_batch(idxs)

        # Convert decord NDArray -> CuPy via DLPack (zero-copy on GPU when supported).
        if hasattr(batch, "to_dlpack"):
            capsule = batch.to_dlpack()
            try:
                out = cp.fromDlpack(capsule)  # CuPy < 13
            except Exception:
                out = cp.from_dlpack(capsule)  # CuPy >= 13
        else:
            out = cp.asarray(batch.asnumpy())

        # Ensure (N,H,W,3) uint8.
        if out.ndim == 3:
            # (N,H,W) -> expand grayscale.
            out = cp.stack([out, out, out], axis=3)
        if out.ndim == 4 and out.shape[3] >= 3:
            out = out[:, :, :, :3]
        if out.dtype != cp.uint8:
            out = out.astype(cp.uint8)

        try:
            if not out.flags.c_contiguous:
                out = cp.ascontiguousarray(out)
        except Exception:
            pass

        return out

    def get_frame(self, t: float) -> np.ndarray:
        """Return a NumPy uint8 RGB frame (public API compatibility)."""
        from moviepy.video.tools import cupy_utils

        cp = cupy_utils.cupy()
        return cp.asnumpy(self.get_frame_gpu(t))

    @property
    def lastread(self):
        # Keep attribute for compatibility; read the first frame.
        return self.get_frame(0.0)

    def close(self):
        # Decord doesn't require explicit close, but drop references.
        try:
            self._vr = None
        except Exception:
            pass

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass
