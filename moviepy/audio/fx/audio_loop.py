from moviepy.audio.AudioClip import concatenate_audioclips
from moviepy.decorators import audio_video_fx


@audio_video_fx
def audio_loop(clip, n_loops=None, duration=None):
    """Loops over an audio clip.

    Returns an audio clip that plays the given clip either
    `n_loops` times, or during `duration` seconds.

    Examples
    --------

    >>> from moviepy import *
    >>> videoclip = VideoFileClip('myvideo.mp4')
    >>> music = AudioFileClip('music.ogg')
    >>> audio = afx.audio_loop( music, duration=videoclip.duration)
    >>> videoclip.with_audio(audio)

    """
    if duration is not None:
        n_loops = int(duration / clip.duration) + 1
        return concatenate_audioclips(n_loops * [clip]).with_duration(duration)

    return concatenate_audioclips(n_loops * [clip])
