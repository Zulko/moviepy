from moviepy.audio.AudioClip import AudioArrayClip
from numpy import transpose, array
from librosa.effects import time_stretch as lr_time_stretch


def time_stretch(audioclip, factor):
    """Stretches audioclip by factor."""
    snd_array = audioclip.to_soundarray()

    if audioclip.nchannels == 1:
        stretched_array = lr_time_stretch(snd_array, factor)
    else:
        stretched_array = transpose( array([lr_time_stretch(snd_array[:,0], factor), lr_time_stretch(snd_array[:,1], factor)]) )

    return AudioArrayClip(stretched_array, fps=44100)

