from ..AudioClip import concatenate_audioclips

def audio_loop(audioclip, nloops=None, duration=None):
    """ Loops over an audio clip.

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

    if duration is not None:

        nloops = int( duration/ audioclip.duration)+1
        return concatenate_audioclips(nloops*[audioclip]).set_duration(duration)
    
    else:

        return concatenate_audioclips(nloops*[audioclip])
    
