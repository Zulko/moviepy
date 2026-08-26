"""Optional Numba-accelerated blending helpers.

This module is internal-only.

If `numba` is not installed (or fails to import), MoviePy will fall back to
its NumPy implementation.
"""

from __future__ import annotations

from functools import lru_cache


@lru_cache(maxsize=1)
def _numba():
    try:
        import numba

        return numba
    except Exception:
        return None


def is_available() -> bool:
    return _numba() is not None


@lru_cache(maxsize=1)
def _kernels():
    numba = _numba()
    if numba is None:
        return None

    import numpy as np

    njit = numba.njit

    @njit(cache=True, fastmath=True)
    def blend_over_opaque_u8(
        bg,
        frame,
        alpha,
        y1_bg,
        y2_bg,
        x1_bg,
        x2_bg,
        y1_clip,
        y2_clip,
        x1_clip,
        x2_clip,
    ):
        """Blend frame over bg in-place assuming bg is fully opaque.

        bg: uint8 HxWx3
        frame: uint8 hxwx3
        alpha: float mask hxw in [0,1]
        """
        h = y2_bg - y1_bg
        w = x2_bg - x1_bg
        for dy in range(h):
            by = y1_bg + dy
            cy = y1_clip + dy
            for dx in range(w):
                bx = x1_bg + dx
                cx = x1_clip + dx
                a = alpha[cy, cx]
                if a <= 0.0:
                    continue
                if a >= 1.0:
                    bg[by, bx, 0] = frame[cy, cx, 0]
                    bg[by, bx, 1] = frame[cy, cx, 1]
                    bg[by, bx, 2] = frame[cy, cx, 2]
                    continue

                inv = 1.0 - a
                bg[by, bx, 0] = np.uint8(
                    np.rint(frame[cy, cx, 0] * a + bg[by, bx, 0] * inv)
                )
                bg[by, bx, 1] = np.uint8(
                    np.rint(frame[cy, cx, 1] * a + bg[by, bx, 1] * inv)
                )
                bg[by, bx, 2] = np.uint8(
                    np.rint(frame[cy, cx, 2] * a + bg[by, bx, 2] * inv)
                )

    @njit(cache=True, fastmath=True)
    def blend_over_with_masks_u8(
        bg,
        bg_mask,
        frame,
        alpha_clip,
        y1_bg,
        y2_bg,
        x1_bg,
        x2_bg,
        y1_clip,
        y2_clip,
        x1_clip,
        x2_clip,
    ):
        """Blend frame over bg in-place, updating bg_mask in-place.

        bg: uint8 HxWx3
        bg_mask: float HxW in [0,1]
        frame: uint8 hxwx3
        alpha_clip: float hxw in [0,1]
        """
        h = y2_bg - y1_bg
        w = x2_bg - x1_bg
        for dy in range(h):
            by = y1_bg + dy
            cy = y1_clip + dy
            for dx in range(w):
                bx = x1_bg + dx
                cx = x1_clip + dx
                a_clip = alpha_clip[cy, cx]
                a_bg = bg_mask[by, bx]

                if a_clip <= 0.0:
                    continue

                # final_alpha = a_clip + a_bg * (1 - a_clip)
                final_a = a_clip + a_bg * (1.0 - a_clip)
                bg_mask[by, bx] = final_a

                safe = final_a
                if safe == 0.0:
                    safe = 1.0

                # (frame*a_clip + bg*a_bg*(1-a_clip)) / safe
                inv_clip = 1.0 - a_clip
                w_bg = a_bg * inv_clip

                bg[by, bx, 0] = np.uint8(
                    np.rint((frame[cy, cx, 0] * a_clip + bg[by, bx, 0] * w_bg) / safe)
                )
                bg[by, bx, 1] = np.uint8(
                    np.rint((frame[cy, cx, 1] * a_clip + bg[by, bx, 1] * w_bg) / safe)
                )
                bg[by, bx, 2] = np.uint8(
                    np.rint((frame[cy, cx, 2] * a_clip + bg[by, bx, 2] * w_bg) / safe)
                )

    return blend_over_opaque_u8, blend_over_with_masks_u8


def blend_over_opaque_u8(*args, **kwargs):
    kernels = _kernels()
    if kernels is None:
        raise RuntimeError("Numba kernels are unavailable")
    return kernels[0](*args, **kwargs)


def blend_over_with_masks_u8(*args, **kwargs):
    kernels = _kernels()
    if kernels is None:
        raise RuntimeError("Numba kernels are unavailable")
    return kernels[1](*args, **kwargs)
