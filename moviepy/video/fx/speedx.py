from moviepy.decorators import apply_to_mask,apply_to_audio
from moviepy.audio.AudioClip import AudioArrayClip
from librosa.effects import time_stretch


def _stretch_audio(audioclip, factor):
    """Stretches audioclip by factor."""
    sound_array = audioclip.to_soundarray()

    if audioclip.nchannels == 1:
        stretched_array = time_stretch(sound_array, factor)
    else:
        stretched_array = np.transpose( np.array([time_stretch(sound_array[:,0], factor), time_stretch(sound_array[:,1], factor)]) )

    return AudioArrayClip(stretched_array, fps=44100)


def speedx(clip, factor = None, final_duration=None, stretch_audio=True):
    """
    Returns a clip playing the current clip but at a speed multiplied
    by ``factor``. Instead of factor one can indicate the desired
    ``final_duration`` of the clip, and the factor will be automatically
    computed.
    The same effect is applied to the clip's audio and mask if any.
    """

    if final_duration:
        factor = 1.0* clip.duration / final_duration

    newclip = clip.fl_time(lambda t: factor * t, apply_to=['mask', 'audio'])

    if clip.duration is not None:
        newclip = newclip.set_duration(1.0 * clip.duration / factor)

    if stretch_audio:
        stretched_audio = _stretch_audio(clip.audio, factor)
        newclip = newclip.set_audio(stretched_audio)

    return newclip
