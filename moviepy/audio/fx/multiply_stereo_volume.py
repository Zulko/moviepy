from moviepy.decorators import audio_video_fx


@audio_video_fx
def multiply_stereo_volume(clip, left=1, right=1):
    """For a stereo audioclip, this function enables to change the volume
    of the left and right channel separately (with the factors `left`
    and `right`). Makes a stereo audio clip in which the volume of left
    and right is controllable.

    Examples
    --------

    >>> from moviepy import AudioFileClip
    >>> music = AudioFileClip('music.ogg')
    >>> audio_r = music.multiply_stereo_volume(left=0, right=1)  # mute left channel/s
    >>> audio_h = music.multiply_stereo_volume(left=0.5, right=0.5)  # half audio
    """

    def stereo_volume(get_frame, t):
        frame = get_frame(t)
        if len(frame) == 1:  # mono
            frame *= left if left is not None else right
        else:  # stereo, stereo surround...
            for i in range(len(frame[0])):  # odd channels are left
                frame[:, i] *= left if i % 2 == 0 else right
        return frame

    return clip.transform(stereo_volume, keep_duration=True)
