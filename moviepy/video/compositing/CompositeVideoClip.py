import numpy as np
from moviepy.video.VideoClip import VideoClip, ColorClip
from moviepy.audio.AudioClip import CompositeAudioClip

#  CompositeVideoClip

class CompositeVideoClip(VideoClip):

    """ 
    
    A VideoClip made of other videoclips displayed together. This is the
    base class for most compositions.
    
    Parameters

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

    transparent
      If False, the clips are overlaid on a surface
      of the color `bg_color`. If True, the clips are overlaid on
      a transparent surface, so that all pixels that are transparent
      for all clips will be transparent in the composite clip. More
      precisely, the mask of the composite clip is then the composite
      of the masks of the different clips. Only use `transparent=True`
      when you intend to use your composite clip as part of another
      composite clip and you care about its transparency.
      
    """

    def __init__(self, clips, size=None, bg_color=None, transparent=False,
                 ismask=False):
                     
        if size is None:
            size = clips[0].size
        
        if bg_color is None:
            bg_color = 0.0 if ismask else (0, 0, 0)
        
        VideoClip.__init__(self)
        
        self.size = size
        self.ismask = ismask
        self.clips = clips
        self.transparent = transparent
        self.bg_color = bg_color
        self.bg = ColorClip(size, col=self.bg_color).get_frame(0)
        
        # compute duration
        ends = [c.end for c in self.clips]
        if not any([(e is None) for e in ends]):
            self.duration = max(ends)
            self.end = max(ends)

        # compute audio
        audioclips = [v.audio for v in self.clips if v.audio != None]
        if len(audioclips) > 0:
            self.audio = CompositeAudioClip(audioclips)

        # compute mask
        if transparent:
            maskclips = [c.mask.set_pos(c.pos) for c in self.clips
                         if c.mask is not None]
            if maskclips != []:
                self.mask = CompositeVideoClip(maskclips,self.size,
                                        transparent=False, ismask=True)

        def gf(t):
            """ The clips playing at time `t` are blitted over one
                another. """

            f = self.bg
            for c in self.playing_clips(t):
                    f = c.blit_on(f, t)
            return f

        self.get_frame = gf

    def playing_clips(self, t=0):
        """ Returns a list of the clips in the composite clips that are
            actually playing at the given time `t`. """
        return [c for c in self.clips if c.is_playing(t)]



def clips_array(array, rows_widths=None, cols_widths=None,
                transparent = False, bg_color = (0,0,0)):
    
    array = np.array(array)
    sizes_array = np.array([[c.size for c in line] for line in array])
    
    if rows_widths == None:
        rows_widths = sizes_array[:,:,1].max(axis=1)
    if cols_widths == None:
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
                                          transparent = transparent,
                                          bg_color = (bg_color)).
                                     set_duration(clip.duration))
                
            array[i,j] = clip.set_pos((x,y))           
                 
    return CompositeVideoClip(array.flatten(), size = (xx[-1],yy[-1]),
                              transparent=transparent,
                              bg_color = bg_color)
    
    
