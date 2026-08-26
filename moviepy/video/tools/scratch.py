"""Internal scratch-buffer pool.

This is intentionally *not* a global frame cache.

We only reuse temporary working arrays that never escape to user code.
Buffers are stored per-thread to avoid cross-thread corruption.
"""

from __future__ import annotations

import os
import threading

import numpy as np


_tls = threading.local()


def _max_cache_bytes() -> int:
    """Maximum size (bytes) for a single cached scratch buffer.

    Defaults to 64MB to avoid keeping very large 4K float buffers resident.
    Set env var MOVIEPY_SCRATCH_CACHE_MAX_MB to override (0 disables caching).
    """
    val = os.environ.get("MOVIEPY_SCRATCH_CACHE_MAX_MB", "64")
    try:
        mb = float(val)
    except Exception:
        mb = 64.0
    if mb <= 0:
        return 0
    return int(mb * 1024 * 1024)


def _store() -> dict[object, np.ndarray]:
    store = getattr(_tls, "store", None)
    if store is None:
        store = {}
        _tls.store = store
    return store


def clear() -> None:
    """Clear all cached scratch buffers for the current thread."""
    store = getattr(_tls, "store", None)
    if store is not None:
        store.clear()


def get_array(key: str, shape: tuple[int, ...], dtype) -> np.ndarray:
    """Get an array of at least `shape` and `dtype` for the current thread.

    The returned array is a view with exactly `shape`.
    """
    if any(s < 0 for s in shape):
        raise ValueError(f"Invalid shape: {shape}")

    dtype = np.dtype(dtype)
    store_key = (key, dtype.str, len(shape))

    max_bytes = _max_cache_bytes()
    requested_bytes = int(np.prod(shape, dtype=np.int64)) * dtype.itemsize
    cache_allowed = (max_bytes > 0) and (requested_bytes <= max_bytes)

    store = _store() if cache_allowed else None
    arr = store.get(store_key) if store is not None else None

    if (arr is not None) and (max_bytes > 0) and (arr.nbytes > max_bytes):
        # Cached buffer is now over budget (e.g., env var changed).
        try:
            del store[store_key]
        except Exception:
            pass
        arr = None

    if arr is None or arr.dtype != dtype or arr.ndim != len(shape):
        arr = np.empty(shape, dtype=dtype)
        if store is not None:
            store[store_key] = arr
        return arr

    if any(req > cur for req, cur in zip(shape, arr.shape)):
        new_shape = tuple(max(req, cur) for req, cur in zip(shape, arr.shape))
        new_bytes = int(np.prod(new_shape, dtype=np.int64)) * dtype.itemsize
        if (max_bytes > 0) and (new_bytes > max_bytes):
            # Grow would exceed cache budget: return an uncached exact-size buffer.
            return np.empty(shape, dtype=dtype)

        arr = np.empty(new_shape, dtype=dtype)
        if store is not None:
            store[store_key] = arr

    slices = tuple(slice(0, s) for s in shape)
    return arr[slices]


def get_float32(key: str, shape: tuple[int, ...]) -> np.ndarray:
    return get_array(key, shape, np.float32)
