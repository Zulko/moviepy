from ..AudioClip import concatenate_audioclips


def audio_loop(audioclip, n_loops=None, duration=None):
    """Loops over an audio clip.

    Returns an audio clip that plays the given clip either
    `n_loops` times, or during `duration` seconds.

    Examples
    ========

    >>> from moviepy.editor import *
    >>> videoclip = VideoFileClip('myvideo.mp4')
    >>> music = AudioFileClip('music.ogg')
    >>> audio = afx.audio_loop( music, duration=videoclip.duration)
    >>> videoclip.with_audio(audio)

    """

    if duration is not None:

        n_loops = int(duration / audioclip.duration) + 1
        return concatenate_audioclips(n_loops * [audioclip]).with_duration(duration)

    else:

        return concatenate_audioclips(n_loops * [audioclip])
