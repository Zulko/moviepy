import numpy as np

from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.tools import deprecated_version_of
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.on_color import on_color
from moviepy.video.VideoClip import ColorClip, VideoClip

try:               # Python 2
   reduce
except NameError:  # Python 3
   from functools import reduce


def concatenate_videoclips(clips, method="chain", transition=None,
                           bg_color=None, ismask=False, padding = 0):
    """ Concatenates several video clips

    Returns a video clip made by clip by concatenating several video clips.
    (Concatenated means that they will be played one after another).

    There are two methods:

    - method="chain": will produce a clip that simply outputs
      the frames of the succesive clips, without any correction if they are
      not of the same size of anything. If none of the clips have masks the
      resulting clip has no mask, else the mask is a concatenation of masks
      (using completely opaque for clips that don't have masks, obviously).
      If you have clips of different size and you want to write directly the
      result of the concatenation to a file, use the method "compose" instead.

    - method="compose", if the clips do not have the same
      resolution, the final resolution will be such that no clip has
       to be resized.
       As a consequence the final clip has the height of the highest
       clip and the width of the widest clip of the list. All the
       clips with smaller dimensions will appear centered. The border
       will be transparent if mask=True, else it will be of the
       color specified by ``bg_color``.

    The clip with the highest FPS will be the FPS of the result clip.

    Parameters
    -----------
    clips
      A list of video clips which must all have their ``duration``
      attributes set.
    method
      "chain" or "compose": see above.
    transition
      A clip that will be played between each two clips of the list.

    bg_color
      Only for method='compose'. Color of the background.
      Set to None for a transparent clip

    padding
      Only for method='compose'. Duration during two consecutive clips.
      Note that for negative padding, a clip will partly play at the same
      time as the clip it follows (negative padding is cool for clips who fade
      in on one another). A non-null padding automatically sets the method to
      `compose`.

    """

    if transition is not None:
        l = [[v, transition] for v in clips[:-1]]
        clips = reduce(lambda x, y: x + y, l) + [clips[-1]]
        transition = None

    tt = np.cumsum([0] + [c.duration for c in clips])

    sizes = [v.size for v in clips]

    w = max(r[0] for r in sizes)
    h = max(r[1] for r in sizes)

    tt = np.maximum(0, tt + padding * np.arange(len(tt)))

    if method == "chain":
        def make_frame(t):
            i = max([i for i, e in enumerate(tt) if e <= t])
            return clips[i].get_frame(t - tt[i])

        def get_mask(c):
            mask = c.mask or ColorClip([1, 1], color=1, ismask=True)
            if mask.duration is None:
               mask.duration = c.duration
            return mask

        result = VideoClip(ismask = ismask, make_frame = make_frame)
        if any([c.mask is not None for c in clips]):
            masks = [get_mask(c) for c in clips]
            result.mask = concatenate_videoclips(masks, method="chain",
                                                 ismask=True)
            result.clips = clips
    elif method == "compose":
        result = CompositeVideoClip( [c.set_start(t).set_position('center')
                                for (c, t) in zip(clips, tt)],
               size = (w, h), bg_color=bg_color, ismask=ismask)
    else:
        raise Exception("Moviepy Error: The 'method' argument of "
                        "concatenate_videoclips must be 'chain' or 'compose'")

    result.tt = tt

    result.start_times = tt[:-1]
    result.start, result.duration, result.end = 0, tt[-1] , tt[-1]

    audio_t = [(c.audio, t) for c, t in zip(clips,tt) if c.audio is not None]
    if audio_t:
        result.audio = CompositeAudioClip([a.set_start(t)
                                for a,t in audio_t])

    fpss = [c.fps for c in clips if getattr(c, 'fps', None) is not None]
    result.fps = max(fpss) if fpss else None
    return result


concatenate = deprecated_version_of(concatenate_videoclips,
                                    oldname="concatenate")
