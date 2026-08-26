"""Optional GPU-native video encoding via NVIDIA NVENC (PyNvCodec/PyNvVideoCodec).

This module is internal and best-effort:
- It is attempted when GPU encoding isn't disabled. With backend=auto (default),
  we try NVENC opportunistically and fall back silently on any failure.
- It never changes MoviePy's public API.
- It always falls back to the existing FFmpeg stdin writer on any failure.

The goal is to avoid downloading per-frame RGB data back to the CPU for encoding.
We still rely on FFmpeg for container muxing and (optionally) audio.
"""

from __future__ import annotations

import os
import subprocess as sp
from dataclasses import dataclass
from typing import Optional

import numpy as np

from moviepy.config import FFMPEG_BINARY
from moviepy.tools import (
    cross_platform_popen_params,
    ffmpeg_escape_filename,
    subprocess_call,
)


def _env_flag(name: str, default: str = "0") -> bool:
    val = os.environ.get(name, default)
    return str(val).strip().lower() not in {"0", "false", "no", "off", ""}


def _disabled_value(val: str) -> bool:
    v = (val or "").strip().lower()
    return v in {"0", "false", "no", "off", "none", "disable", "disabled"}


def gpu_encode_backend() -> str:
    return (os.getenv("MOVIEPY_GPU_ENCODE_BACKEND") or "auto").strip().lower()


def is_enabled() -> bool:
    """Whether GPU-native encoding should be attempted.

    GPU encoding can be disabled via env vars. Otherwise, NVENC is attempted
    opportunistically (backend=auto) or explicitly (backend=nvenc/pynv/pynvcodec).
    """
    if _env_flag("MOVIEPY_DISABLE_GPU", "0"):
        return False
    if _env_flag("MOVIEPY_DISABLE_GPU_ENCODE", "0"):
        return False

    backend = gpu_encode_backend()
    if _disabled_value(backend):
        return False

    if backend not in {"auto", "pynvcodec", "pynv", "nvenc"}:
        return False

    # If the user explicitly requested an NVENC backend, treat that as opt-in
    # even when GPU render isn't enabled. We'll still fall back safely if any
    # required pieces aren't available.
    if backend in {"pynvcodec", "pynv", "nvenc"}:
        return True

    return True


def _strict() -> bool:
    return _env_flag("MOVIEPY_GPU_ENCODE_STRICT", "0")


def _parse_gpu_id() -> int:
    try:
        return int(os.getenv("MOVIEPY_GPU_DEVICE", "0"))
    except Exception:
        return 0


def _map_codec(codec: str) -> Optional[str]:
    """Map MoviePy/FFmpeg-ish codec strings to PyNvEncoder codec values."""
    c = (codec or "").strip().lower()
    if not c:
        return None
    if "hevc" in c or "h265" in c or "libx265" in c or c == "h265_nvenc":
        return "hevc"
    if "h264" in c or "x264" in c or "libx264" in c or c == "h264_nvenc":
        return "h264"
    return None


def _map_nvenc_preset(preset: str) -> str:
    """Best-effort mapping from FFmpeg preset names to NVENC preset IDs."""
    p = (preset or "").strip().lower()
    return {
        "ultrafast": "P1",
        "superfast": "P2",
        "veryfast": "P3",
        "faster": "P4",
        "fast": "P4",
        "medium": "P5",
        "slow": "P6",
        "slower": "P7",
        "veryslow": "P7",
        "placebo": "P7",
    }.get(p, "P5")


def _parse_color_matrix(val: Optional[str]) -> str:
    v = (val or "").strip().lower()
    if v in {"bt709", "709"}:
        return "bt709"
    return "bt601"


def _parse_color_range(val: Optional[str]) -> str:
    v = (val or "").strip().lower()
    if v in {"jpeg", "full", "pc", "fullrange"}:
        return "jpeg"
    return "mpeg"


def _gpu_color_settings_for_clip(clip) -> tuple[str, str]:
    # Clip-level overrides (internal attrs) take precedence.
    matrix = getattr(clip, "_gpu_color_matrix", None)
    crange = getattr(clip, "_gpu_color_range", None)
    if matrix is None:
        matrix = os.getenv("MOVIEPY_GPU_COLOR_MATRIX")
    if crange is None:
        crange = os.getenv("MOVIEPY_GPU_COLOR_RANGE")
    return _parse_color_matrix(matrix), _parse_color_range(crange)


_RGB_TO_NV12_KERNEL_CACHE = {}


def _get_rgb_to_nv12_kernel(cp, *, matrix: str, crange: str):
    key = (matrix, crange)
    k = _RGB_TO_NV12_KERNEL_CACHE.get(key)
    if k is not None:
        return k

    # Integer coefficient sets.
    # Limited (MPEG): Y has +16 offset, coefficients scaled for 219/255 range.
    # Full (JPEG): Y has no offset, coefficients are full-range.
    if matrix == "bt709" and crange == "mpeg":
        y_r, y_g, y_b, y_off = 47, 157, 16, 16
        u_r, u_g, u_b, u_off = -26, -87, 112, 128
        v_r, v_g, v_b, v_off = 112, -102, -10, 128
    elif matrix == "bt709" and crange == "jpeg":
        y_r, y_g, y_b, y_off = 54, 183, 18, 0
        u_r, u_g, u_b, u_off = -29, -99, 128, 128
        v_r, v_g, v_b, v_off = 128, -116, -12, 128
    elif matrix == "bt601" and crange == "jpeg":
        y_r, y_g, y_b, y_off = 77, 150, 29, 0
        u_r, u_g, u_b, u_off = -43, -85, 128, 128
        v_r, v_g, v_b, v_off = 128, -107, -21, 128
    else:
        # Default: BT.601 limited/MPEG.
        y_r, y_g, y_b, y_off = 66, 129, 25, 16
        u_r, u_g, u_b, u_off = -38, -74, 112, 128
        v_r, v_g, v_b, v_off = 112, -94, -18, 128

    src = rf'''
    extern "C" __device__ __forceinline__ unsigned char clamp_u8(int v) {{
        return (unsigned char)(v < 0 ? 0 : (v > 255 ? 255 : v));
    }}

    extern "C" __global__ void rgb_to_nv12_u8(
        const unsigned char* __restrict__ src,
        unsigned char* __restrict__ y_plane,
        unsigned char* __restrict__ uv_plane,
        const int w,
        const int h,
        const int src_pitch,
        const int y_pitch,
        const int uv_pitch
    ) {{
        int bx = (int)(blockIdx.x * blockDim.x + threadIdx.x);
        int by = (int)(blockIdx.y * blockDim.y + threadIdx.y);
        int x = bx * 2;
        int y = by * 2;
        if (x + 1 >= w || y + 1 >= h) return;

        const unsigned char* row0 = src + y * src_pitch;
        const unsigned char* row1 = src + (y + 1) * src_pitch;

        int idx00 = x * 3;
        int idx01 = (x + 1) * 3;
        int idx10 = x * 3;
        int idx11 = (x + 1) * 3;

        int r00 = (int)row0[idx00 + 0];
        int g00 = (int)row0[idx00 + 1];
        int b00 = (int)row0[idx00 + 2];

        int r01 = (int)row0[idx01 + 0];
        int g01 = (int)row0[idx01 + 1];
        int b01 = (int)row0[idx01 + 2];

        int r10 = (int)row1[idx10 + 0];
        int g10 = (int)row1[idx10 + 1];
        int b10 = (int)row1[idx10 + 2];

        int r11 = (int)row1[idx11 + 0];
        int g11 = (int)row1[idx11 + 1];
        int b11 = (int)row1[idx11 + 2];

        int y00 = (({y_r} * r00 + {y_g} * g00 + {y_b} * b00 + 128) >> 8) + {y_off};
        int y01 = (({y_r} * r01 + {y_g} * g01 + {y_b} * b01 + 128) >> 8) + {y_off};
        int y10 = (({y_r} * r10 + {y_g} * g10 + {y_b} * b10 + 128) >> 8) + {y_off};
        int y11 = (({y_r} * r11 + {y_g} * g11 + {y_b} * b11 + 128) >> 8) + {y_off};

        unsigned char* y_row0 = y_plane + y * y_pitch;
        unsigned char* y_row1 = y_plane + (y + 1) * y_pitch;
        y_row0[x] = clamp_u8(y00);
        y_row0[x + 1] = clamp_u8(y01);
        y_row1[x] = clamp_u8(y10);
        y_row1[x + 1] = clamp_u8(y11);

        int u00 = (({u_r} * r00 + {u_g} * g00 + {u_b} * b00 + 128) >> 8) + {u_off};
        int u01 = (({u_r} * r01 + {u_g} * g01 + {u_b} * b01 + 128) >> 8) + {u_off};
        int u10 = (({u_r} * r10 + {u_g} * g10 + {u_b} * b10 + 128) >> 8) + {u_off};
        int u11 = (({u_r} * r11 + {u_g} * g11 + {u_b} * b11 + 128) >> 8) + {u_off};

        int v00 = (({v_r} * r00 + {v_g} * g00 + {v_b} * b00 + 128) >> 8) + {v_off};
        int v01 = (({v_r} * r01 + {v_g} * g01 + {v_b} * b01 + 128) >> 8) + {v_off};
        int v10 = (({v_r} * r10 + {v_g} * g10 + {v_b} * b10 + 128) >> 8) + {v_off};
        int v11 = (({v_r} * r11 + {v_g} * g11 + {v_b} * b11 + 128) >> 8) + {v_off};

        int u = (u00 + u01 + u10 + u11 + 2) >> 2;
        int v = (v00 + v01 + v10 + v11 + 2) >> 2;

        unsigned char* uv_row = uv_plane + by * uv_pitch;
        uv_row[x] = clamp_u8(u);
        uv_row[x + 1] = clamp_u8(v);
    }}
    '''

    k = cp.RawKernel(src, "rgb_to_nv12_u8")
    _RGB_TO_NV12_KERNEL_CACHE[key] = k
    return k


def _import_nvc():
    """Import NV codec bindings.

    Prefer legacy `PyNvCodec` when available, otherwise fall back to NVIDIA's
    pip-distributed successor `PyNvVideoCodec`.
    """

    # Windows: PyNvVideoCodec relies on CUDA/driver DLLs being discoverable.
    # Notably, current wheels depend on the CUDA 12 runtime DLL `cudart64_12.dll`.
    # Make a best-effort attempt to add plausible CUDA runtime directories.
    if os.name == "nt" and hasattr(os, "add_dll_directory"):
        # 1) If installed via pip, `nvidia-cuda-runtime-cu12` provides cudart64_12.dll
        # under `.../site-packages/nvidia/cuda_runtime/bin`.
        try:
            import site

            roots = []
            try:
                roots.append(site.getusersitepackages())
            except Exception:
                pass
            try:
                roots.extend(site.getsitepackages() or [])
            except Exception:
                pass

            for root in roots:
                if not root:
                    continue
                dll_dir = os.path.join(root, "nvidia", "cuda_runtime", "bin")
                try:
                    if os.path.isfile(os.path.join(dll_dir, "cudart64_12.dll")):
                        os.add_dll_directory(dll_dir)
                except Exception:
                    pass
        except Exception:
            pass

        # 2) CUDA Toolkit installs (any version) often provide runtime DLLs under
        # CUDA_PATH\bin\x64 (or sometimes CUDA_PATH\bin).
        cuda_roots = []
        cuda_roots.append(os.environ.get("CUDA_PATH"))
        for name, value in os.environ.items():
            if name.startswith("CUDA_PATH_V") and value:
                cuda_roots.append(value)

        for cuda_root in cuda_roots:
            if not cuda_root:
                continue
            for rel in ("bin", os.path.join("bin", "x64"), os.path.join("lib", "x64")):
                dll_dir = os.path.join(cuda_root, rel)
                try:
                    if os.path.isdir(dll_dir):
                        os.add_dll_directory(dll_dir)
                except Exception:
                    pass

    try:
        import PyNvCodec as nvc  # type: ignore

        return nvc
    except Exception:
        # PyNvVideoCodec currently triggers a DeprecationWarning on Python 3.13+
        # due to internal use of deprecated ast nodes. Silence it here so users
        # don't see noise during normal operation.
        import warnings

        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                category=DeprecationWarning,
                module=r"^PyNvVideoCodec(\\..*)?$",
            )
            import PyNvVideoCodec as nvc  # type: ignore

        return nvc


def _ffmpeg_remux_h26x(
    *,
    input_stream: str,
    output_file: str,
    fps: float,
    is_hevc: bool,
    audiofile: Optional[str],
    audio_codec: Optional[str],
    logger,
) -> None:
    stream_fmt = "hevc" if is_hevc else "h264"
    cmd = [
        FFMPEG_BINARY,
        "-y",
        "-loglevel",
        "error",
        "-r",
        f"{fps:.02f}",
        "-f",
        stream_fmt,
        "-i",
        ffmpeg_escape_filename(input_stream),
    ]

    if audiofile is not None:
        cmd.extend(["-i", ffmpeg_escape_filename(audiofile)])
        cmd.extend(["-c:v", "copy"])
        cmd.extend(["-c:a", audio_codec or "copy"])
    else:
        cmd.extend(["-c:v", "copy", "-an"])

    cmd.append(ffmpeg_escape_filename(output_file))
    subprocess_call(cmd, logger=logger)


class _FFmpegH26xPipeMuxer:
    """Mux an elementary H.264/HEVC stream from stdin into a container via FFmpeg."""

    def __init__(
        self,
        *,
        output_file: str,
        fps: float,
        is_hevc: bool,
        audiofile: Optional[str],
        audio_codec: Optional[str],
        logger,
    ):
        stream_fmt = "hevc" if is_hevc else "h264"
        cmd = [
            FFMPEG_BINARY,
            "-y",
            "-loglevel",
            "error",
            "-r",
            f"{fps:.02f}",
            "-f",
            stream_fmt,
            "-i",
            "pipe:0",
        ]

        if audiofile is not None:
            cmd.extend(["-i", ffmpeg_escape_filename(audiofile)])
            cmd.extend(["-map", "0:v:0", "-map", "1:a:0"])
            cmd.extend(["-c:v", "copy"])
            cmd.extend(["-c:a", audio_codec or "copy"])
        else:
            cmd.extend(["-map", "0:v:0", "-c:v", "copy", "-an"])

        cmd.append(ffmpeg_escape_filename(output_file))

        self._cmd = cmd
        self._logger = logger
        self._proc = None

    def __enter__(self):
        logger = self._logger
        if logger is not None:
            logger(message="MoviePy - Running:\n>>> " + " ".join(self._cmd))

        popen_params = cross_platform_popen_params(
            {"stdout": sp.DEVNULL, "stderr": sp.PIPE, "stdin": sp.PIPE}
        )
        self._proc = sp.Popen(self._cmd, **popen_params)
        assert self._proc.stdin is not None
        return self._proc.stdin

    def __exit__(self, exc_type, exc_val, exc_tb):
        proc = self._proc
        if proc is None:
            return False

        try:
            if proc.stdin is not None:
                try:
                    proc.stdin.close()
                except Exception:
                    pass

            if exc_type is not None:
                try:
                    proc.kill()
                except Exception:
                    pass

            _out, err = proc.communicate()
            if proc.stderr is not None:
                try:
                    proc.stderr.close()
                except Exception:
                    pass

            if exc_type is None and proc.returncode:
                msg = (err or b"").decode("utf8", errors="replace")
                raise IOError(msg)

            return False
        finally:
            self._proc = None


@dataclass
class _EncodeContext:
    gpu_id: int
    width: int
    height: int
    fps: float
    codec: str
    preset: str
    bitrate: Optional[str]


class _SurfaceConverterChain:
    def __init__(self, nvc, width: int, height: int, gpu_id: int, chain):
        self._nvc = nvc
        self._gpu_id = gpu_id
        self._cc = nvc.ColorspaceConversionContext(
            nvc.ColorSpace.BT_601, nvc.ColorRange.MPEG
        )
        self._chain = [
            nvc.PySurfaceConverter(width, height, src, dst, gpu_id)
            for (src, dst) in chain
        ]

    def run(self, surf):
        out = surf
        for cvt in self._chain:
            out = cvt.Execute(out, self._cc)
            if out.Empty():
                raise RuntimeError("GPU colorspace conversion failed")
        # Returning the surface directly avoids an extra device copy.
        return out


def _parse_bitrate_to_bps(bitrate: Optional[str]) -> Optional[int]:
    if not bitrate:
        return None
    if isinstance(bitrate, (int, float)):
        try:
            return int(bitrate)
        except Exception:
            return None

    s = str(bitrate).strip()
    if not s:
        return None

    # Common MoviePy/FFmpeg-style forms: "5000k", "5M", "8000000".
    mult = 1
    last = s[-1].lower()
    if last in {"k", "m", "g"}:
        s_num = s[:-1].strip()
        mult = {"k": 1000, "m": 1000_000, "g": 1000_000_000}[last]
    else:
        s_num = s

    try:
        return int(float(s_num) * mult)
    except Exception:
        return None


class _NV12CudaFrame:
    """PyNvVideoCodec GPU-buffer input frame helper.

    For GPU buffer mode, PyNvVideoCodec expects an object with a `cuda()` method
    that returns CUDA Array Interface dictionaries for each plane.
    """

    def __init__(self, y_plane, uv_plane):
        self._y = y_plane
        self._uv = uv_plane

    def cuda(self):
        return [self._y.__cuda_array_interface__, self._uv.__cuda_array_interface__]


class PyNvVideoCodecNVENCWriter:
    """Write H.264/HEVC using NVENC from CuPy RGB frames (PyNvVideoCodec)."""

    class _Slot:
        __slots__ = ("nv12", "y", "uv", "frame", "conv_done", "encode_done")

        def __init__(self, nv12, y, uv, frame, conv_done, encode_done):
            self.nv12 = nv12
            self.y = y
            self.uv = uv
            self.frame = frame
            self.conv_done = conv_done
            self.encode_done = encode_done

    @staticmethod
    def _create_encoder_best_effort(nvc, width: int, height: int, params: dict):
        """Create a PyNvVideoCodec encoder.

        Tolerates API differences across versions.
        """

        attempts = [
            dict(params),
            {k: v for k, v in params.items() if k != "gpuid"},
            {k: v for k, v in params.items() if k not in {"gpuid", "repeatspspps"}},
            {
                k: v
                for k, v in params.items()
                if k not in {"gpuid", "repeatspspps", "tuning_info"}
            },
            {k: v for k, v in params.items() if k in {"codec", "preset", "fps"}},
            {k: v for k, v in params.items() if k in {"codec", "preset"}},
            {k: v for k, v in params.items() if k in {"codec"}},
        ]

        last_exc = None
        for p in attempts:
            try:
                return nvc.CreateEncoder(width, height, "NV12", False, **p)
            except Exception as exc:  # best-effort; retry with fewer args
                last_exc = exc
                continue

        raise last_exc

    @staticmethod
    def _iter_packets(payload):
        if not payload:
            return
        if isinstance(payload, (bytes, bytearray, memoryview)):
            yield payload
            return
        # Some bindings return a list of packets.
        if isinstance(payload, (list, tuple)):
            for p in payload:
                if p:
                    yield p
            return
        yield payload

    def __init__(
        self,
        *,
        width: int,
        height: int,
        fps: float,
        codec: str,
        preset: str,
        bitrate: Optional[str],
        gpu_id: int,
        color_matrix: str = "bt601",
        color_range: str = "mpeg",
        out,
    ):
        import cupy as cp  # lazy

        nvc = _import_nvc()

        self._cp = cp
        self._nvc = nvc
        self._ctx = _EncodeContext(
            gpu_id=gpu_id,
            width=width,
            height=height,
            fps=fps,
            codec=codec,
            preset=preset,
            bitrate=bitrate,
        )
        self._out = out

        # Explicit streams for conversion/encoding.
        # We keep conversion on a dedicated stream; encode is assumed to run on the
        # default stream (or an internal stream), so we order with CUDA events.
        self._conv_stream = cp.cuda.Stream(non_blocking=True)
        self._pending = []

        # Surface/buffer pool to avoid overwriting an input buffer while NVENC is still
        # consuming it, and to enable overlap between conversion and encode.
        self._pool_size = max(2, int(os.getenv("MOVIEPY_GPU_ENCODE_POOL", "3")))
        self._slots = []
        for _ in range(self._pool_size):
            nv12 = cp.empty((height + height // 2, width), dtype=cp.uint8)
            y = nv12[:height, :]
            uv = nv12[height : height + height // 2, :]
            frame = _NV12CudaFrame(y, uv)
            self._slots.append(
                self._Slot(
                    nv12,
                    y,
                    uv,
                    frame,
                    cp.cuda.Event(),
                    cp.cuda.Event(),
                )
            )
        self._slot_index = 0

        # Kernel: packed HWC RGB -> NV12 (BT.601 limited/MPEG range).
        self._color_matrix = _parse_color_matrix(color_matrix)
        self._color_range = _parse_color_range(color_range)
        self._rgb_to_nv12 = _get_rgb_to_nv12_kernel(
            cp,
            matrix=self._color_matrix,
            crange=self._color_range,
        )

        enc_params = {
            "codec": codec,
            "preset": preset,
            "fps": float(fps),
            "tuning_info": "high_quality",
            # Ensure elementary stream contains headers suitable for muxing.
            "repeatspspps": 1,
        }

        # Try to honor MoviePy's bitrate strings ("5000k", "5M", ...).
        bps = _parse_bitrate_to_bps(bitrate)
        if bps:
            enc_params["bitrate"] = int(bps)

        # Some PyNvVideoCodec APIs use `gpuid` naming (not `gpu_id`).
        enc_params["gpuid"] = int(gpu_id)

        self._enc = self._create_encoder_best_effort(nvc, width, height, enc_params)

    def _as_nv12_frame_best_effort(self, f):
        cp = self._cp

        # 1) If the user provided a PyNvVideoCodec-style object, accept it.
        if callable(getattr(f, "cuda", None)):
            return f

        # 2) Tuple/list of planes.
        if isinstance(f, (tuple, list)) and len(f) == 2:
            y, uv = f
            if hasattr(y, "__cuda_array_interface__") and hasattr(
                uv, "__cuda_array_interface__"
            ):
                return _NV12CudaFrame(y, uv)

        # 3) Packed NV12 (H+H/2, W) uint8.
        if hasattr(f, "__cuda_array_interface__"):
            if getattr(f, "dtype", None) == cp.uint8 and getattr(f, "ndim", None) == 2:
                h = int(self._ctx.height)
                w = int(self._ctx.width)
                if int(f.shape[0]) == (h + h // 2) and int(f.shape[1]) == w:
                    y = f[:h, :]
                    uv = f[h : h + h // 2, :]
                    return _NV12CudaFrame(y, uv)

        return None

    def _write_payload(self, payload) -> None:
        for pkt in self._iter_packets(payload):
            self._out.write(pkt)

    def write_frame(self, frame_rgb):
        cp = self._cp

        # Direct NV12 acceptance (GPU-native color management / preconversion).
        nv12_obj = self._as_nv12_frame_best_effort(frame_rgb)

        slot = self._slots[self._slot_index]
        self._slot_index = (self._slot_index + 1) % self._pool_size

        # Ensure we don't overwrite a slot that the encoder may still be consuming.
        try:
            cp.cuda.runtime.streamWaitEvent(
                int(self._conv_stream.ptr),
                int(slot.encode_done.ptr),
                0,
            )
        except Exception:
            slot.encode_done.synchronize()

        if nv12_obj is not None:
            # If user provided NV12 planes, we can encode immediately.
            # Use the pipeline queue to preserve overlap semantics.
            self._pending.append((nv12_obj, slot))
            if len(self._pending) <= 1:
                return
            encode_item = self._pending.pop(0)
            frame_obj, enc_slot = encode_item
            self._write_payload(self._enc.Encode(frame_obj))
            try:
                enc_slot.encode_done.record(cp.cuda.Stream.null)
            except Exception:
                enc_slot.encode_done.synchronize()
            return

        f = frame_rgb
        if not hasattr(f, "__cuda_array_interface__"):
            # Best-effort: upload CPU frame to GPU so encoding can still be GPU.
            if isinstance(f, np.ndarray):
                f = cp.asarray(f)
            else:
                raise RuntimeError(
                    "Expected a GPU frame (CUDA array) or a NumPy ndarray"
                )
        if f.ndim != 3 or f.shape[2] < 3:
            raise ValueError(
                "Expected HxWx3 frame, got shape="
                f"{getattr(f, 'shape', None)!r}"
            )
        f = f[:, :, :3]

        with self._conv_stream:
            if f.dtype != cp.uint8:
                f = f.astype(cp.uint8)
            try:
                if not f.flags.c_contiguous:
                    f = cp.ascontiguousarray(f)
            except Exception:
                f = cp.ascontiguousarray(f)

            threads = (16, 16)
            grid = (
                ((self._ctx.width // 2) + threads[0] - 1) // threads[0],
                ((self._ctx.height // 2) + threads[1] - 1) // threads[1],
            )
            self._rgb_to_nv12(
                grid,
                threads,
                (
                    f,
                    slot.y,
                    slot.uv,
                    int(self._ctx.width),
                    int(self._ctx.height),
                    int(f.strides[0]),
                    int(slot.y.strides[0]),
                    int(slot.uv.strides[0]),
                ),
            )
            slot.conv_done.record(self._conv_stream)

        # Queue this slot for encoding; we encode one frame behind to allow
        # conversion and encode to overlap.
        self._pending.append(slot)

        if len(self._pending) <= 1:
            return

        encode_slot = self._pending.pop(0)

        # Ensure conversion finished before giving the buffer to NVENC.
        encode_slot.conv_done.synchronize()

        self._write_payload(self._enc.Encode(encode_slot.frame))

        # Record an event after Encode so we can safely reuse this slot later.
        try:
            encode_slot.encode_done.record(cp.cuda.Stream.null)
        except Exception:
            encode_slot.encode_done.synchronize()

    def write_frames(self, frames):
        """Best-effort batched encode to reduce host syncs.

        Accepts:
        - iterable of frames
        - a CuPy array shaped (N,H,W,3)
        """
        cp = self._cp

        # Normalize iterator.
        if hasattr(frames, "__cuda_array_interface__") and getattr(
            frames, "ndim", None
        ) == 4:
            n = int(frames.shape[0])
            it = (frames[i] for i in range(n))
        elif isinstance(frames, (list, tuple)):
            it = iter(frames)
        else:
            it = iter([frames])

        slots_to_encode = []
        frames_to_encode_direct = []

        # Stage conversions on the conversion stream.
        for f_in in it:
            nv12_obj = self._as_nv12_frame_best_effort(f_in)
            if nv12_obj is not None:
                frames_to_encode_direct.append(nv12_obj)
                continue

            f = f_in
            if not hasattr(f, "__cuda_array_interface__"):
                if isinstance(f, np.ndarray):
                    f = cp.asarray(f)
                else:
                    raise RuntimeError(
                        "Expected a GPU frame (CUDA array) or a NumPy ndarray"
                    )
            if f.ndim != 3 or f.shape[2] < 3:
                raise ValueError(
                    "Expected HxWx3 frame, got shape="
                    f"{getattr(f, 'shape', None)!r}"
                )
            f = f[:, :, :3]

            slot = self._slots[self._slot_index]
            self._slot_index = (self._slot_index + 1) % self._pool_size

            # Ensure slot is not reused while NVENC might still consume it.
            try:
                cp.cuda.runtime.streamWaitEvent(
                    int(self._conv_stream.ptr),
                    int(slot.encode_done.ptr),
                    0,
                )
            except Exception:
                slot.encode_done.synchronize()

            with self._conv_stream:
                if f.dtype != cp.uint8:
                    f = f.astype(cp.uint8)
                try:
                    if not f.flags.c_contiguous:
                        f = cp.ascontiguousarray(f)
                except Exception:
                    f = cp.ascontiguousarray(f)

                threads = (16, 16)
                grid = (
                    ((self._ctx.width // 2) + threads[0] - 1) // threads[0],
                    ((self._ctx.height // 2) + threads[1] - 1) // threads[1],
                )
                self._rgb_to_nv12(
                    grid,
                    threads,
                    (
                        f,
                        slot.y,
                        slot.uv,
                        int(self._ctx.width),
                        int(self._ctx.height),
                        int(f.strides[0]),
                        int(slot.y.strides[0]),
                        int(slot.uv.strides[0]),
                    ),
                )

            slots_to_encode.append(slot)

        # Encode any direct NV12 inputs first.
        for nv12_obj in frames_to_encode_direct:
            self._write_payload(self._enc.Encode(nv12_obj))

        if not slots_to_encode:
            return

        # Single sync per batch instead of per-frame conv_done.synchronize().
        try:
            self._conv_stream.synchronize()
        except Exception:
            cp.cuda.runtime.deviceSynchronize()

        for slot in slots_to_encode:
            self._write_payload(self._enc.Encode(slot.frame))
            try:
                slot.encode_done.record(cp.cuda.Stream.null)
            except Exception:
                slot.encode_done.synchronize()

    def close(self):
        # Drain any queued frames.
        if getattr(self, "_pending", None):
            while self._pending:
                item = self._pending.pop(0)
                if isinstance(item, tuple):
                    frame_obj, slot = item
                    self._write_payload(self._enc.Encode(frame_obj))
                    try:
                        slot.encode_done.record(self._cp.cuda.Stream.null)
                    except Exception:
                        pass
                else:
                    slot = item
                    try:
                        slot.conv_done.synchronize()
                    except Exception:
                        pass
                    self._write_payload(self._enc.Encode(slot.frame))
                    try:
                        slot.encode_done.record(self._cp.cuda.Stream.null)
                    except Exception:
                        pass

        if getattr(self, "_enc", None) is not None:
            self._write_payload(self._enc.EndEncode())
        if getattr(self, "_out", None) is not None:
            try:
                self._out.close()
            finally:
                self._out = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class PyNvCodecNVENCWriter:
    """Write H.264/HEVC using NVENC from CuPy RGB frames."""

    class _Slot:
        __slots__ = ("surface", "y", "uv", "conv_done", "encode_done")

        def __init__(self, surface, y, uv, conv_done, encode_done):
            self.surface = surface
            self.y = y
            self.uv = uv
            self.conv_done = conv_done
            self.encode_done = encode_done

    def __init__(
        self,
        *,
        width: int,
        height: int,
        fps: float,
        codec: str,
        preset: str,
        bitrate: Optional[str],
        gpu_id: int,
        out,
    ):
        import cupy as cp  # lazy
        nvc = _import_nvc()

        self._cp = cp
        self._nvc = nvc
        self._ctx = _EncodeContext(
            gpu_id=gpu_id,
            width=width,
            height=height,
            fps=fps,
            codec=codec,
            preset=preset,
            bitrate=bitrate,
        )
        self._out = out
        self._packet = np.ndarray(shape=(0,), dtype=np.uint8)

        self._conv_stream = cp.cuda.Stream(non_blocking=True)
        self._pending = []

        self._pool_size = max(2, int(os.getenv("MOVIEPY_GPU_ENCODE_POOL", "3")))
        self._slots = []
        self._slot_index = 0

        def _map_nv12_surface(surface):
            pitch = int(surface.Pitch())
            y_ptr = None
            uv_ptr = None
            try:
                y_ptr = int(surface.PlanePtr(0).GpuMem())
                uv_ptr = int(surface.PlanePtr(1).GpuMem())
            except Exception:
                pass

            if y_ptr is not None and uv_ptr is not None:
                y_bytes = pitch * height
                uv_bytes = pitch * (height // 2)
                y_unowned = cp.cuda.UnownedMemory(int(y_ptr), int(y_bytes), surface)
                uv_unowned = cp.cuda.UnownedMemory(int(uv_ptr), int(uv_bytes), surface)
                y_memptr = cp.cuda.MemoryPointer(y_unowned, 0)
                uv_memptr = cp.cuda.MemoryPointer(uv_unowned, 0)
                y = cp.ndarray(
                    (height, pitch),
                    dtype=cp.uint8,
                    memptr=y_memptr,
                    strides=(pitch, 1),
                )
                uv = cp.ndarray(
                    (height // 2, pitch),
                    dtype=cp.uint8,
                    memptr=uv_memptr,
                    strides=(pitch, 1),
                )
                return pitch, y, uv

            dst_ptr = int(surface.PlanePtr().GpuMem())
            buf_bytes = pitch * (height + height // 2)
            unowned = cp.cuda.UnownedMemory(dst_ptr, buf_bytes, surface)
            memptr = cp.cuda.MemoryPointer(unowned, 0)
            view = cp.ndarray(
                (height + height // 2, pitch),
                dtype=cp.uint8,
                memptr=memptr,
                strides=(pitch, 1),
            )
            return (
                pitch,
                view[:height, :],
                view[height : height + height // 2, :],
            )

        for _ in range(self._pool_size):
            surface = nvc.Surface.Make(nvc.PixelFormat.NV12, width, height, gpu_id)
            self._surface_nv12_pitch, y, uv = _map_nv12_surface(surface)
            self._slots.append(
                self._Slot(
                    surface,
                    y,
                    uv,
                    cp.cuda.Event(),
                    cp.cuda.Event(),
                )
            )

        # Kernel: packed HWC RGB -> NV12 (BT.601 limited/MPEG range).
        self._rgb_to_nv12 = cp.RawKernel(
            r'''
            extern "C" __device__ __forceinline__ unsigned char clamp_u8(int v) {
                return (unsigned char)(v < 0 ? 0 : (v > 255 ? 255 : v));
            }

            extern "C" __global__ void rgb_to_nv12_bt601_mpeg_u8(
                const unsigned char* __restrict__ src,
                unsigned char* __restrict__ y_plane,
                unsigned char* __restrict__ uv_plane,
                const int w,
                const int h,
                const int src_pitch,
                const int y_pitch,
                const int uv_pitch
            ) {
                int bx = (int)(blockIdx.x * blockDim.x + threadIdx.x);
                int by = (int)(blockIdx.y * blockDim.y + threadIdx.y);
                int x = bx * 2;
                int y = by * 2;
                if (x + 1 >= w || y + 1 >= h) return;

                const unsigned char* row0 = src + y * src_pitch;
                const unsigned char* row1 = src + (y + 1) * src_pitch;

                int idx00 = x * 3;
                int idx01 = (x + 1) * 3;
                int idx10 = x * 3;
                int idx11 = (x + 1) * 3;

                int r00 = (int)row0[idx00 + 0];
                int g00 = (int)row0[idx00 + 1];
                int b00 = (int)row0[idx00 + 2];

                int r01 = (int)row0[idx01 + 0];
                int g01 = (int)row0[idx01 + 1];
                int b01 = (int)row0[idx01 + 2];

                int r10 = (int)row1[idx10 + 0];
                int g10 = (int)row1[idx10 + 1];
                int b10 = (int)row1[idx10 + 2];

                int r11 = (int)row1[idx11 + 0];
                int g11 = (int)row1[idx11 + 1];
                int b11 = (int)row1[idx11 + 2];

                // BT.601 limited range (MPEG):
                // Y  = (( 66R +129G + 25B +128) >> 8) + 16
                // U  = ((-38R - 74G +112B +128) >> 8) +128
                // V  = ((112R - 94G - 18B +128) >> 8) +128
                int y00 = ((66 * r00 + 129 * g00 + 25 * b00 + 128) >> 8) + 16;
                int y01 = ((66 * r01 + 129 * g01 + 25 * b01 + 128) >> 8) + 16;
                int y10 = ((66 * r10 + 129 * g10 + 25 * b10 + 128) >> 8) + 16;
                int y11 = ((66 * r11 + 129 * g11 + 25 * b11 + 128) >> 8) + 16;

                unsigned char* y_row0 = y_plane + y * y_pitch;
                unsigned char* y_row1 = y_plane + (y + 1) * y_pitch;
                y_row0[x] = clamp_u8(y00);
                y_row0[x + 1] = clamp_u8(y01);
                y_row1[x] = clamp_u8(y10);
                y_row1[x + 1] = clamp_u8(y11);

                int u00 = ((-38 * r00 - 74 * g00 + 112 * b00 + 128) >> 8) + 128;
                int u01 = ((-38 * r01 - 74 * g01 + 112 * b01 + 128) >> 8) + 128;
                int u10 = ((-38 * r10 - 74 * g10 + 112 * b10 + 128) >> 8) + 128;
                int u11 = ((-38 * r11 - 74 * g11 + 112 * b11 + 128) >> 8) + 128;

                int v00 = ((112 * r00 - 94 * g00 - 18 * b00 + 128) >> 8) + 128;
                int v01 = ((112 * r01 - 94 * g01 - 18 * b01 + 128) >> 8) + 128;
                int v10 = ((112 * r10 - 94 * g10 - 18 * b10 + 128) >> 8) + 128;
                int v11 = ((112 * r11 - 94 * g11 - 18 * b11 + 128) >> 8) + 128;

                // Average chroma over 2x2 block with rounding.
                int u = (u00 + u01 + u10 + u11 + 2) >> 2;
                int v = (v00 + v01 + v10 + v11 + 2) >> 2;

                unsigned char* uv_row = uv_plane + by * uv_pitch;
                uv_row[x] = clamp_u8(u);
                uv_row[x + 1] = clamp_u8(v);
            }
            ''',
            "rgb_to_nv12_bt601_mpeg_u8",
        )

        res = f"{width}x{height}"
        enc_params = {
            "codec": codec,
            "preset": preset,
            "s": res,
            "tuning_info": "high_quality",
        }
        if bitrate:
            enc_params["bitrate"] = bitrate

        self._enc = nvc.PyNvEncoder(enc_params, gpu_id)

    def _cupy_rgb_to_surface_nv12(self, frame):
        cp = self._cp
        f_in = frame
        if not hasattr(f_in, "__cuda_array_interface__"):
            if isinstance(f_in, np.ndarray):
                f_in = cp.asarray(f_in)
            else:
                raise RuntimeError(
                    "Expected a GPU frame (CUDA array) or a NumPy ndarray"
                )

        f = f_in
        if f.ndim != 3 or f.shape[2] < 3:
            raise ValueError(
                "Expected HxWx3 frame, got shape="
                f"{getattr(f, 'shape', None)!r}"
            )
        f = f[:, :, :3]
        if f.dtype != cp.uint8:
            f = f.astype(cp.uint8)
        try:
            if not f.flags.c_contiguous:
                f = cp.ascontiguousarray(f)
        except Exception:
            f = cp.ascontiguousarray(f)

        slot = self._slots[self._slot_index]
        self._slot_index = (self._slot_index + 1) % self._pool_size

        try:
            cp.cuda.runtime.streamWaitEvent(
                int(self._conv_stream.ptr),
                int(slot.encode_done.ptr),
                0,
            )
        except Exception:
            slot.encode_done.synchronize()

        with self._conv_stream:
            threads = (16, 16)
            grid = (
                ((self._ctx.width // 2) + threads[0] - 1) // threads[0],
                ((self._ctx.height // 2) + threads[1] - 1) // threads[1],
            )
            self._rgb_to_nv12(
                grid,
                threads,
                (
                    f,
                    slot.y,
                    slot.uv,
                    int(self._ctx.width),
                    int(self._ctx.height),
                    int(f.strides[0]),
                    int(slot.y.strides[0]),
                    int(slot.uv.strides[0]),
                ),
            )
            slot.conv_done.record(self._conv_stream)

        return slot.surface, slot

    def _write_packet(self):
        if self._packet.size:
            self._out.write(memoryview(self._packet))

    def write_frame(self, frame_rgb):
        surface_nv12, slot = self._cupy_rgb_to_surface_nv12(frame_rgb)
        self._pending.append((surface_nv12, slot))

        if len(self._pending) <= 1:
            return

        surface_to_encode, encode_slot = self._pending.pop(0)
        encode_slot.conv_done.synchronize()
        success = self._enc.EncodeSingleSurface(surface_to_encode, self._packet)
        if success:
            self._write_packet()

        # Mark slot reusable.
        try:
            encode_slot.encode_done.record(self._cp.cuda.Stream.null)
        except Exception:
            pass

    def write_frames(self, frames):
        """Best-effort batched encode to reduce host syncs."""
        cp = self._cp

        if hasattr(frames, "__cuda_array_interface__") and getattr(
            frames, "ndim", None
        ) == 4:
            n = int(frames.shape[0])
            it = (frames[i] for i in range(n))
        elif isinstance(frames, (list, tuple)):
            it = iter(frames)
        else:
            it = iter([frames])

        pending_local = []
        for f in it:
            surface_nv12, slot = self._cupy_rgb_to_surface_nv12(f)
            pending_local.append((surface_nv12, slot))

        if not pending_local:
            return

        # One sync per batch.
        try:
            self._conv_stream.synchronize()
        except Exception:
            cp.cuda.runtime.deviceSynchronize()

        for surface_nv12, slot in pending_local:
            success = self._enc.EncodeSingleSurface(surface_nv12, self._packet)
            if success:
                self._write_packet()
            try:
                slot.encode_done.record(cp.cuda.Stream.null)
            except Exception:
                pass

    def close(self):
        if getattr(self, "_pending", None):
            while self._pending:
                surface_to_encode, slot = self._pending.pop(0)
                try:
                    slot.conv_done.synchronize()
                except Exception:
                    pass
                success = self._enc.EncodeSingleSurface(surface_to_encode, self._packet)
                if success:
                    self._write_packet()
                try:
                    slot.encode_done.record(self._cp.cuda.Stream.null)
                except Exception:
                    pass

        if getattr(self, "_enc", None) is not None:
            while self._enc.FlushSinglePacket(self._packet):
                self._write_packet()
        if getattr(self, "_out", None) is not None:
            try:
                self._out.close()
            finally:
                self._out = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def try_write_video_pynvcodec(
    *,
    clip,
    filename: str,
    fps: float,
    codec: str,
    bitrate: Optional[str],
    preset: str,
    audiofile: Optional[str],
    audio_codec: Optional[str],
    logger,
    gpu_render=None,
    pixel_format: Optional[str],
) -> bool:
    """Best-effort: encode via NVENC from GPU frames, then mux via FFmpeg.

    Returns True if the file was written. Returns False to indicate the caller
    should fall back to the standard FFmpeg stdin writer.
    """
    if not is_enabled():
        return False

    backend = gpu_encode_backend()
    if backend not in {"auto", "pynvcodec", "pynv", "nvenc"}:
        # Unknown/unsupported backend: do not attempt.
        return False

    if clip.mask is not None:
        # NVENC path doesn't preserve alpha.
        return False

    if pixel_format is not None:
        # Respect user request; NVENC path uses NV12 internally.
        return False

    mapped = _map_codec(codec)
    if mapped is None:
        return False

    # NV12 requires even dimensions.
    if (clip.w % 2) or (clip.h % 2):
        return False

    gpu_id = _parse_gpu_id()
    nvenc_preset = _map_nvenc_preset(preset)
    color_matrix, color_range = _gpu_color_settings_for_clip(clip)

    try:
        # These imports are intentionally inside the try so missing optional deps
        # just trigger a fallback.
        import cupy as _cp  # noqa: F401
        nvc = _import_nvc()

        with _FFmpegH26xPipeMuxer(
            output_file=filename,
            fps=float(fps),
            is_hevc=(mapped == "hevc"),
            audiofile=audiofile,
            audio_codec=audio_codec,
            logger=logger,
        ) as mux_stdin:
            writer_cls = (
                PyNvCodecNVENCWriter
                if hasattr(nvc, "Surface")
                else PyNvVideoCodecNVENCWriter
            )

            with writer_cls(
                width=clip.w,
                height=clip.h,
                fps=float(fps),
                codec=mapped,
                preset=nvenc_preset,
                bitrate=bitrate,
                gpu_id=gpu_id,
                color_matrix=color_matrix,
                color_range=color_range,
                out=mux_stdin,
            ) as writer:
                n_frames = int(clip.duration * fps)
                iter_bar = logger.iter_bar
                gpu_fn = getattr(clip, "_gpu_frame_function", None)
                wants_nv12 = (getattr(clip, "_gpu_frame_format", None) == "nv12")

                batch = 0
                try:
                    batch = int(os.getenv("MOVIEPY_GPU_ENCODE_BATCH", "0") or "0")
                except Exception:
                    batch = 0

                # Auto default: use pool size (keeps batching modest and aligned
                # with buffer reuse). User can always force 1 to disable.
                if batch <= 0:
                    try:
                        batch = int(os.getenv("MOVIEPY_GPU_ENCODE_POOL", "3") or "3")
                    except Exception:
                        batch = 3
                batch = max(1, int(batch))

                batch_safe = bool(getattr(clip, "_gpu_batch_safe", False))
                batch_decode = getattr(clip, "_gpu_frame_function_batch_by_index", None)
                can_batch_decode = (
                    batch_safe and callable(batch_decode) and (not wants_nv12)
                )

                decode_batch = 0
                try:
                    decode_batch = int(
                        os.getenv("MOVIEPY_GPU_DECODE_BATCH", "0") or "0"
                    )
                except Exception:
                    decode_batch = 0
                if decode_batch <= 0:
                    # Auto default: if batch decode is available, use a small
                    # chunk (pool-aligned) even if encode batching is disabled.
                    if can_batch_decode:
                        try:
                            decode_batch = int(
                                os.getenv("MOVIEPY_GPU_ENCODE_POOL", "3")
                                or "3"
                            )
                        except Exception:
                            decode_batch = 3
                    else:
                        decode_batch = 1
                decode_batch = max(1, int(decode_batch))

                def _get_frame_for_nvenc(t):
                    # If the clip explicitly provides a GPU frame function and
                    # is tagged as NV12, prefer that output (which may be an
                    # NV12 carrier object, NV12 planes, or packed NV12).
                    if wants_nv12 and (gpu_fn is not None):
                        return gpu_fn(t)

                    # Otherwise, still prefer the GPU frame function if it
                    # returns a CUDA array (decode/process on GPU) to avoid
                    # CPU downloads between stages.
                    if gpu_fn is not None:
                        try:
                            v = gpu_fn(t)
                            if hasattr(v, "__cuda_array_interface__") or callable(
                                getattr(v, "cuda", None)
                            ):
                                return v
                        except Exception:
                            pass

                    if gpu_render is not None:
                        return gpu_render.get_frame_for_export_uint8_gpu(clip, t)

                    return clip.get_frame(t)

                fps_f = float(fps)

                if (batch <= 1) and (
                    not (can_batch_decode and (decode_batch > 1))
                ):
                    for frame_index in iter_bar(frame_index=range(n_frames)):
                        t = np.float64(frame_index) / fps_f
                        frame = _get_frame_for_nvenc(t)
                        writer.write_frame(frame)
                else:
                    # Iterate in chunks to reduce per-frame host syncs.
                    chunk = batch
                    if (batch <= 1) and can_batch_decode and (decode_batch > 1):
                        # Decode in batches but still encode per-frame.
                        chunk = decode_batch

                    for start in iter_bar(frame_index=range(0, n_frames, chunk)):
                        end = min(n_frames, int(start) + chunk)
                        idxs = list(range(int(start), int(end)))

                        if can_batch_decode:
                            frames = batch_decode(idxs)
                            if (batch > 1) and hasattr(
                                writer, "write_frames"
                            ):
                                writer.write_frames(frames)
                            else:
                                for i in range(int(frames.shape[0])):
                                    writer.write_frame(frames[i])
                            continue

                        frames = []
                        for fi in idxs:
                            t = np.float64(fi) / fps_f
                            frames.append(_get_frame_for_nvenc(t))

                        if (batch > 1) and hasattr(
                            writer, "write_frames"
                        ):
                            writer.write_frames(frames)
                        else:
                            for fr in frames:
                                writer.write_frame(fr)

        return True
    except Exception:
        if _strict() or backend in {"pynvcodec", "pynv", "nvenc"}:
            raise
        return False
