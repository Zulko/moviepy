"""contains the errors that can be raised by the video IO functions."""


class VideoCorruptedError(RuntimeError):
    """Error raised when a video file is corrupted."""
