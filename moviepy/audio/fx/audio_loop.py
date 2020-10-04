from ..AudioClip import concatenate_audioclips


def audio_loop(clip, nloops=None, duration=None):
    """Loops over an audio clip.

    Returns an audio clip that plays the given clip either
    `nloops` times, or during `duration` seconds.

    Examples
    ========

    >>> from moviepy.editor import *
    >>> videoclip = VideoFileClip('myvideo.mp4')
    >>> music = AudioFileClip('music.ogg')
    >>> audio = afx.audio_loop( music, duration=videoclip.duration)
    >>> videoclip.set_audio(audio)

    """
    try:
        clip = clip.audio
    except AttributeError:
        # assume it's already an audioclip
        pass

    if duration is not None:
        nloops = int(duration / clip.duration) + 1
        return concatenate_audioclips(nloops * [clip]).set_duration(duration)

    return concatenate_audioclips(nloops * [clip])
