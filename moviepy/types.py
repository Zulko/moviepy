from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Tuple, Union, TypeVar

    import proglog
    from typing_extensions import TypeAlias, Literal, ParamSpec, Concatenate

    from moviepy.Clip import Clip
    from moviepy.audio.AudioClip import AudioClip
    from moviepy.video.VideoClip import VideoClip

    P = ParamSpec("P")
    T = TypeVar("T")
    _ClipFunc: TypeAlias = Callable[Concatenate[T, P], T]
    ClipFunc: TypeAlias = _ClipFunc[Clip, P]
    AudioClipFunc: TypeAlias = _ClipFunc[AudioClip, P]
    VideoClipFunc: TypeAlias = _ClipFunc[VideoClip, P]
    Logger: TypeAlias = Union[Literal["bar"], proglog.ProgressLogger, None]
    NBytes: TypeAlias = Literal[1, 2, 4]
    NChannels: TypeAlias = Literal[1, 2]
    ScreenSide: TypeAlias = Literal["top", "bottom", "left", "right"]
    Time: TypeAlias = Union[float, Tuple[int, int], Tuple[int, int, int], str]
