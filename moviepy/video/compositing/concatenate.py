import numpy as np

from moviepy.video.VideoClip import VideoClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.AudioClip import CompositeAudioClip

from moviepy.video.compositing.on_color import on_color 

def concatenate(clipslist, method="chain", transition=None, bg_color=(0, 0, 0),
                transparent=False, ismask=False, padding = 0):
    """ Concatenates several video clips
    
    Returns a video clip made by clip by concatenating several video clips.
    (Concatenated means that they will be played one after another).
    
    There are two methods: method="chain" will produce a clip that simply outputs
    the frames of the succesive clips, without any correction if they are
    not of the same size of anything.

    With method="compose", if the clips do not have the same
    resolution, the final resolution will be such that no clip has
    to be resized.
    As a consequence the final clip has the height of the highest
    clip and the width of the widest clip of the list. All the
    clips with smaller dimensions will appear centered. The border
    will be transparent if mask=True, else it will be of the
    color specified by ``bg_color``.

    Returns a VideoClip instance if all clips have the same size and
    there is no transition, else a composite clip.
    
    Parameters
    -----------

    clipslist
      A list of video clips which must all have their ``duration``
      attributes set.

    method
      "chain" or "compose": see above.

    transition
      A clip that will be played between each two clips of the list.  
    
    bg_color
      Color of the background, if any.

    transparent
      If True, the resulting clip's mask will be the concatenation of
      the masks of the clips in the list. If the clips do not have the
      same resolution, the border around the smaller clips will be
      transparent.

    padding
      Duration during two consecutive clips. If negative, a clip will
      play at the same time as the clip it follows. A non-null
      padding automatically sets the method to `compose`.
           
    """

    if transition != None:
        l = [[v, transition] for v in clipslist[:-1]]
        clipslist = reduce(lambda x, y: x + y, l) + [clipslist[-1]]
        transition = None

    
    tt = np.cumsum([0] + [c.duration for c in clipslist])

    sizes = [v.size for v in clipslist]


    w = max([r[0] for r in sizes])
    h = max([r[1] for r in sizes])

    tt = np.maximum(0, tt + padding*np.arange(len(tt)))
    
    if method == "chain":
        def gf(t):
            i = max([i for i, e in enumerate(tt) if e <= t])
            return clipslist[i].get_frame(t - tt[i])
            result.get_frame = gf
        result = VideoClip(ismask = ismask, get_frame = gf)
        if transparent:
          clips_w_masks = [(c.add_mask() if c.mask is None else c) for c in clips]
          masks = [c.mask for c in clips_w_masks]
          result.mask = concatenate(masks, method="chain", ismask=True)


    elif method == "compose":
        result = CompositeVideoClip( [c.set_start(t).set_pos('center')
                                for (c, t) in zip(clipslist, tt)],
               size = (w, h), bg_color=bg_color, ismask=ismask,
               transparent=transparent )

    result.tt = tt
    result.clipslist = clipslist
    result.start_times = tt[:-1]
    result.start, result.duration, result.end = 0, tt[-1] , tt[-1]
    
    audio_t = [(c.audio,t) for c,t in zip(clipslist,tt) if c.audio!=None]
    if len(audio_t)>0:
        result.audio = CompositeAudioClip([a.set_start(t)
                                for a,t in audio_t])
    return result
