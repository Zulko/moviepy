import numpy as np
from moviepy.video.VideoClip import VideoClip, ColorClip
from moviepy.audio.AudioClip import CompositeAudioClip

#  CompositeVideoClip

class CompositeVideoClip(VideoClip):

    """ 
    
    A VideoClip made of other videoclips displayed together. This is the
    base class for most compositions.
    
    Parameters
    ----------

    size
      The size (height x width) of the final clip.

    clips
      A list of videoclips. Each clip of the list will
      be displayed below the clips appearing after it in the list.
      For each clip:
       
      - The attribute ``pos`` determines where the clip is placed.
          See ``VideoClip.set_pos``
      - The mask of the clip determines which parts are visible.
        
      Finally, if all the clips in the list have their ``duration``
      attribute set, then the duration of the composite video clip
      is computed automatically

    bg_color
      Color for the unmasked and unfilled regions. Set to None for these
      regions to be transparent (will be slower).

    use_bgclip
      Set to True if the first clip in the list should be used as the
      'background' on which all other clips are blitted. That first clip must
      have the same size as the final clip. If it has no transparency, the final
      clip will have no mask. 
    
    If all clips with a fps attribute have the same fps, it becomes the fps of
    the result.

    """

    def __init__(self, clips, size=None, bg_color=None, use_bgclip=False,
                 ismask=False):

        if size is None:
            size = clips[0].size

        
        if use_bgclip and (clips[0].mask is None):
            transparent = False
        else:
            transparent = (bg_color is None)
        
        if bg_color is None:
            bg_color = 0.0 if ismask else (0, 0, 0)

        
        fps_list = list(set([c.fps for c in clips if hasattr(c,'fps')]))
        if len(fps_list)==1:
            self.fps= fps_list[0]

        VideoClip.__init__(self)
        
        self.size = size
        self.ismask = ismask
        self.clips = clips
        self.bg_color = bg_color

        if use_bgclip:
            self.bg = clips[0]
            self.clips = clips[1:]
        else:
            self.clips = clips
            self.bg = ColorClip(size, col=self.bg_color)

        
        
        # compute duration
        ends = [c.end for c in self.clips]
        if not any([(e is None) for e in ends]):
            self.duration = max(ends)
            self.end = max(ends)

        # compute audio
        audioclips = [v.audio for v in self.clips if v.audio is not None]
        if len(audioclips) > 0:
            self.audio = CompositeAudioClip(audioclips)

        # compute mask if necessary
        if transparent:
            maskclips = [(c.mask if (c.mask is not None) else
                          c.add_mask().mask).set_pos(c.pos)
                          for c in self.clips]

            self.mask = CompositeVideoClip(maskclips,self.size, ismask=True,
                                               bg_color=0.0)

        def make_frame(t):
            """ The clips playing at time `t` are blitted over one
                another. """

            f = self.bg.get_frame(t)
            for c in self.playing_clips(t):
                    f = c.blit_on(f, t)
            return f

        self.make_frame = make_frame

    def playing_clips(self, t=0):
        """ Returns a list of the clips in the composite clips that are
            actually playing at the given time `t`. """
        return [c for c in self.clips if c.is_playing(t)]



def clips_array(array, rows_widths=None, cols_widths=None,
                bg_color = None):

    """

    rows_widths
      widths of the different rows in pixels. If None, is set automatically.

    cols_widths
      widths of the different colums in pixels. If None, is set automatically.

    cols_widths
    
    bg_color
       Fill color for the masked and unfilled regions. Set to None for these
       regions to be transparent (will be slower).

    """
    
    array = np.array(array)
    sizes_array = np.array([[c.size for c in line] for line in array])
    
    # find row width and col_widths automatically if not provided
    if rows_widths is None:
        rows_widths = sizes_array[:,:,1].max(axis=1)
    if cols_widths is None:
        cols_widths = sizes_array[:,:,0].max(axis=0)
    
    xx = np.cumsum([0]+list(cols_widths)) 
    yy = np.cumsum([0]+list(rows_widths))
    
    for j,(x,cw) in list(enumerate(zip(xx[:-1],cols_widths))):
        for i,(y,rw) in list(enumerate(zip(yy[:-1],rows_widths))):
            clip = array[i,j]
            w,h = clip.size
            if (w < cw) or (h < rw):
                clip = (CompositeVideoClip([clip.set_pos('center')],
                                          size = (cw,rw),
                                          bg_color = bg_color).
                                     set_duration(clip.duration))
                
            array[i,j] = clip.set_pos((x,y))
                 
    return CompositeVideoClip(array.flatten(), size = (xx[-1],yy[-1]),
                              bg_color = bg_color)
    
    
