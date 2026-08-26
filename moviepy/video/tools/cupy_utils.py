"""Internal CuPy/CUDA helpers.

This module centralizes best-effort CUDA DLL setup (Windows) and CuPy
availability/usability checks. It is intentionally conservative:

- Never requires CuPy as an import-time dependency.
- Never raises on failure; callers should fall back to CPU paths.
"""

from __future__ import annotations

import os
import site
from typing import Any


_CUPY_USABLE: bool | None = None


def is_cuda_array(x: Any) -> bool:
    return hasattr(x, "__cuda_array_interface__")


def _windows_cuda_dll_setup() -> None:
    """Best-effort CUDA DLL setup for Windows.

    CuPy can import successfully but fail later when it needs NVRTC/NVJIT
    DLLs. Adding CUDA Toolkit and pip runtime DLL directories helps.
    """
    if os.name != "nt":
        return

    cuda_root = os.environ.get("CUDA_PATH") or os.environ.get("CUDA_HOME")
    if not cuda_root:
        versioned = [
            (k, v)
            for k, v in os.environ.items()
            if k.startswith("CUDA_PATH_V") and v
        ]
        if versioned:
            cuda_root = sorted(versioned, key=lambda kv: kv[0])[-1][1]
            os.environ.setdefault("CUDA_PATH", cuda_root)

    candidates: list[str] = []
    if cuda_root:
        candidates.extend(
            [
                os.path.join(cuda_root, "bin"),
                os.path.join(cuda_root, "bin", "x64"),
                os.path.join(cuda_root, "bin", "x86_64"),
            ]
        )

    # Pip-installed NVIDIA runtime layout (if present).
    for sp in site.getsitepackages():
        candidates.extend(
            [
                os.path.join(sp, "nvidia", "cu13", "bin"),
                os.path.join(sp, "nvidia", "cu13", "bin", "x86_64"),
                os.path.join(sp, "nvidia", "cu12", "bin"),
                os.path.join(sp, "nvidia", "cu12", "bin", "x86_64"),
            ]
        )

    for d in candidates:
        try:
            if d and os.path.isdir(d):
                os.add_dll_directory(d)
        except Exception:
            pass


def try_import_cupy() -> Any:
    """Return the imported cupy module, or None if unavailable."""
    try:
        _windows_cuda_dll_setup()
        import cupy as cp

        return cp
    except Exception:
        return None


def _cupy_is_usable(cp: Any) -> bool:
    """Return True if CuPy can actually execute kernels."""
    try:
        try:
            if int(cp.cuda.runtime.getDeviceCount()) <= 0:
                return False
        except Exception:
            # Some setups fail here but still work; rely on kernel test.
            pass

        a = cp.zeros((1,), dtype=cp.uint8)
        b = a.astype(cp.float32)
        b += 1.0
        cp.cuda.runtime.deviceSynchronize()
        return True
    except Exception:
        return False


def is_cupy_usable() -> bool:
    """Cached CuPy runtime usability check."""
    global _CUPY_USABLE
    if _CUPY_USABLE is not None:
        return bool(_CUPY_USABLE)

    if os.environ.get("MOVIEPY_DISABLE_GPU"):
        _CUPY_USABLE = False
        return False

    cp = try_import_cupy()
    if cp is None:
        _CUPY_USABLE = False
        return False

    _CUPY_USABLE = bool(_cupy_is_usable(cp))
    return bool(_CUPY_USABLE)


def cupy() -> Any:
    """Return cupy module if usable, else raise ImportError."""
    cp = try_import_cupy()
    if cp is None:
        raise ImportError("cupy is not available")
    return cp
