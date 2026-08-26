"""Video reader based on OpenCV.

This module provides an internal alternative to the ffmpeg pipe reader.

Public APIs are unchanged; VideoFileClip selects a backend internally and will
fall back to ffmpeg if OpenCV cannot open/read the file.
"""

from __future__ import annotations

import os
import warnings

import numpy as np

from moviepy.video.io.ffmpeg_reader import ffmpeg_parse_infos


class OpenCV_VideoReader:
    """Class for video reading with OpenCV (cv2.VideoCapture)."""

    def __init__(
        self,
        filename,
        decode_file=True,
        print_infos=False,
        bufsize=None,  # kept for signature parity with FFMPEG_VideoReader
        pixel_format="rgb24",
        check_duration=True,
        target_resolution=None,
        resize_algo="bicubic",
        fps_source="fps",
        infos=None,
        prefer_hwaccel=True,
    ):
        if pixel_format and pixel_format.lower().endswith("a"):
            raise ValueError(
                "OpenCV_VideoReader does not support alpha (rgba) decoding."
            )

        self.filename = filename
        self.cap = None

        if infos is None:
            infos = ffmpeg_parse_infos(
                filename,
                check_duration=check_duration,
                fps_source=fps_source,
                decode_file=decode_file,
                print_infos=print_infos,
            )

        self.fps = infos.get("video_fps", 1.0) or 1.0
        self._raw_size = infos.get("video_size", (1, 1))
        if isinstance(self._raw_size, (list, tuple)):
            self.size = list(self._raw_size)
        else:
            self.size = self._raw_size
        self._rotation_tag = infos.get("video_rotation", 0) or 0
        self._rotation_apply = 0

        # Match ffmpeg's auto-rotation behavior.
        # Some OpenCV backends already auto-rotate; we detect that at runtime.
        abs_rotation = abs(self._rotation_tag)
        self.rotation = abs_rotation
        if abs_rotation in (90, 270):
            self.size = [self.size[1], self.size[0]]

        if target_resolution:
            if None in target_resolution:
                ratio = 1
                for idx, target in enumerate(target_resolution):
                    if target:
                        ratio = target / self.size[idx]
                self.size = [int(self.size[0] * ratio), int(self.size[1] * ratio)]
            else:
                self.size = list(target_resolution)

        self.resize_algo = resize_algo
        self.duration = infos.get("video_duration", 0.0)
        self.ffmpeg_duration = infos.get("duration", 0.0)
        self.n_frames = infos.get("video_n_frames", 0)
        self.bitrate = infos.get("video_bitrate", 0)
        self.infos = infos

        self.pixel_format = pixel_format
        self.depth = 3

        self._needs_resizer = target_resolution is not None

        self._cv2 = None
        self._prefer_hwaccel = bool(prefer_hwaccel)
        self.initialize()

    def _require_cv2(self):
        if self._cv2 is None:
            import cv2

            self._cv2 = cv2
        return self._cv2

    def _postprocess_frame(self, frame):
        cv2 = self._require_cv2()

        # OpenCV returns BGR; convert to RGB.
        if frame.ndim == 3 and frame.shape[2] >= 3:
            frame = np.ascontiguousarray(frame[:, :, ::-1])
        else:
            frame = np.ascontiguousarray(frame)

        # Apply rotation to match ffmpeg auto-rotate (only if needed).
        rot = int(self._rotation_apply) % 360 if self._rotation_apply else 0
        if rot == 90:
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        elif rot == 180:
            frame = cv2.rotate(frame, cv2.ROTATE_180)
        elif rot == 270:
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif rot not in (0,):
            # Unknown/odd rotation; ignore to avoid surprising behavior.
            pass

        if self._needs_resizer and (tuple(frame.shape[1::-1]) != tuple(self.size)):
            interpolation = cv2.INTER_CUBIC
            if self.resize_algo in {"bilinear", "fast_bilinear"}:
                interpolation = cv2.INTER_LINEAR
            frame = cv2.resize(frame, tuple(self.size), interpolation=interpolation)

        # Ensure uint8 output like ffmpeg rawvideo path.
        if frame.dtype != np.uint8:
            frame = frame.astype(np.uint8, copy=False)

        return frame

    def initialize(self, start_time=0):
        self.close(delete_lastread=False)

        cv2 = self._require_cv2()

        self.cap = None

        def _open_cap(api_preference=None, params=None):
            # Newer OpenCV supports passing params to select hwaccel.
            try:
                if api_preference is None and params is None:
                    return cv2.VideoCapture(self.filename)
                if params is None:
                    return cv2.VideoCapture(self.filename, api_preference)
                return cv2.VideoCapture(self.filename, api_preference, params)
            except TypeError:
                if api_preference is None:
                    return cv2.VideoCapture(self.filename)
                return cv2.VideoCapture(self.filename, api_preference)

        def _hw_params_any():
            if not hasattr(cv2, "CAP_PROP_HW_ACCELERATION"):
                return None
            accel_any = getattr(cv2, "VIDEO_ACCELERATION_ANY", 1)
            return [cv2.CAP_PROP_HW_ACCELERATION, accel_any]

        if self._prefer_hwaccel:
            params = _hw_params_any()
            # Prefer FFmpeg backend when present, otherwise use default backend.
            if hasattr(cv2, "CAP_FFMPEG"):
                self.cap = _open_cap(cv2.CAP_FFMPEG, params=params)
            if (self.cap is None) or (not self.cap.isOpened()):
                self.cap = _open_cap(None, params=params)

        if (self.cap is None) or (not self.cap.isOpened()):
            if hasattr(cv2, "CAP_FFMPEG"):
                self.cap = _open_cap(cv2.CAP_FFMPEG)
            if (self.cap is None) or (not self.cap.isOpened()):
                self.cap = _open_cap()

        # Some builds only accept hwaccel via set() after opening.
        if self._prefer_hwaccel and hasattr(cv2, "CAP_PROP_HW_ACCELERATION"):
            try:
                accel_any = getattr(cv2, "VIDEO_ACCELERATION_ANY", 1)
                self.cap.set(cv2.CAP_PROP_HW_ACCELERATION, accel_any)
            except Exception:
                pass

        if not self.cap or not self.cap.isOpened():
            raise IOError(f"Could not open video file with OpenCV: {self.filename}")

        # Reduce internal buffering where supported to lower RAM usage.
        # Not all backends honor this property.
        if hasattr(cv2, "CAP_PROP_BUFFERSIZE"):
            try:
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            except Exception:
                pass

        # If the backend indicates it already auto-rotates, do not rotate again.
        orientation_auto = None
        if hasattr(cv2, "CAP_PROP_ORIENTATION_AUTO"):
            try:
                orientation_auto = self.cap.get(cv2.CAP_PROP_ORIENTATION_AUTO)
            except Exception:
                orientation_auto = None

        rot = int(round(self._rotation_tag)) if self._rotation_tag else 0
        if rot:
            rot = rot % 360

        self._rotation_apply = rot

        self.pos = self.get_frame_number(start_time)
        if self.pos != 0:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, float(self.pos))

        ok, frame = self.cap.read()
        if not ok or frame is None:
            raise IOError(
                "MoviePy error: failed to read the first frame of video file "
                f"{self.filename}."
            )

        # Detect OpenCV auto-rotation for 90/270 cases by comparing raw frame shape
        # with metadata. When auto-rotation is enabled, OpenCV typically swaps the
        # dimensions already.
        try:
            raw_w, raw_h = int(self._raw_size[0]), int(self._raw_size[1])
        except Exception:
            raw_w, raw_h = 0, 0

        if orientation_auto not in (None, 0, 0.0):
            self._rotation_apply = 0
        elif self._rotation_apply in (90, 270) and raw_w and raw_h:
            if tuple(frame.shape[:2]) == (raw_w, raw_h):
                # Frame is already (h,w) == (raw_w, raw_h) => dimensions swapped.
                self._rotation_apply = 0

        self.last_read = self._postprocess_frame(frame)

        # Trust the processed frame dimensions for downstream writer sizing.
        self.size = list(self.last_read.shape[1::-1])
        self.pos += 1

        # EOF/warn state (reset on re-init).
        self._eof = False
        self._eof_pos = None
        self._warned_eof = False

    def skip_frames(self, n=1):
        if not self.cap:
            self.initialize(0)

        # Use grab() to advance without decoding.
        advanced = 0
        for _ in range(int(n)):
            ok = self.cap.grab()
            if not ok:
                self._eof = True
                if self._eof_pos is None:
                    self._eof_pos = self.pos
                break
            advanced += 1
        self.pos += advanced

    def read_frame(self):
        if not self.cap:
            self.initialize(0)

        if getattr(self, "_eof", False):
            # Do not warn repeatedly: keep returning last frame.
            self.pos += 1
            return self.last_read

        ok, frame = self.cap.read()
        if not ok or frame is None:
            warn_eof = os.environ.get("MOVIEPY_OPENCV_EOF_WARNING", "0")
            warn_eof_str = str(warn_eof).strip().lower()
            warn_eof = warn_eof_str not in {"0", "false", "no", "off", ""}

            if warn_eof and (not getattr(self, "_warned_eof", False)):
                warnings.warn(
                    (
                        "In file %s, failed to read frame index %d. "
                        "Using the last valid frame instead."
                    )
                    % (self.filename, self.pos),
                    UserWarning,
                )
                self._warned_eof = True
            self._eof = True
            if self._eof_pos is None:
                self._eof_pos = self.pos
            if not hasattr(self, "last_read"):
                raise IOError(
                    (
                        "MoviePy error: failed to read the first frame of "
                        f"video file {self.filename}. That might mean that the file is "
                        "corrupted."
                    )
                )
            result = self.last_read
        else:
            result = self._postprocess_frame(frame)
            self.last_read = result

        self.pos += 1
        return result

    def get_frame(self, t):
        pos = self.get_frame_number(t) + 1

        if not self.cap:
            self.initialize(t)
            return self.last_read

        if pos == self.pos:
            return self.last_read
        elif (
            getattr(self, "_eof", False)
            and (self._eof_pos is not None)
            and (pos >= self._eof_pos)
        ):
            return self.last_read
        elif (pos < self.pos) or (pos > self.pos + 100):
            self.initialize(t)
            return self.last_read
        else:
            self.skip_frames(pos - self.pos - 1)
            return self.read_frame()

    @property
    def lastread(self):
        return self.last_read

    def get_frame_number(self, t):
        return int(self.fps * t + 0.00001)

    def close(self, delete_lastread=True):
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None

        if delete_lastread and hasattr(self, "last_read"):
            del self.last_read

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass
