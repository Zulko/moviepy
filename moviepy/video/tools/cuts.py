""" This module contains everything that can help automatize
the cuts in MoviePy """

from moviepy.decorators import use_clip_fps_by_default

import numpy as np

@use_clip_fps_by_default
def find_video_period(clip,fps=None,tmin=.3):
    """ Finds the period of a video based on frames correlation """
    

    frame = lambda t: clip.get_frame(t).flatten()
    tt = np.arange(tmin,clip.duration,1.0/ fps)[1:]
    ref = frame(0)
    corrs = [ np.corrcoef(ref, frame(t))[0,1] for t in tt]
    return tt[np.argmax(corrs)]


@use_clip_fps_by_default
def detect_scenes(clip=None, luminosities=None, thr=10,
                  progress_bar=False, fps=None):
    
    """ Detects scenes of a clip based on luminosity changes.
    
    Note that for large clip this may take some time
    
    Returns
    --------
    cuts, luminosities
      cuts is a series of cuts [(0,t1), (t1,t2),...(...,tf)]
      luminosities are the luminosities computed for each
      frame of the clip.
    
    Parameters
    -----------
    
    clip
      A video clip. Can be None if a list of luminosities is
      provided instead. If provided, the luminosity of each
      frame of the clip will be computed. If the clip has no
      'fps' attribute, you must provide it.
    
    luminosities
      A list of luminosities, e.g. returned by detect_scenes
      in a previous run.
    
    thr
      Determines a threshold above which the 'luminosity jumps'
      will be considered as scene changes. A scene change is defined
      as a change between 2 consecutive frames that is larger than
      (avg * thr) where avg is the average of the absolute changes
      between consecutive frames.
      
    progress_bar
      We all love progress bars ! Here is one for you, in option.
      
    fps
      Must be provided if you provide no clip or a clip without
      fps attribute.
    
    
    
    
    """
        
    if luminosities is None:
        luminosities = [f.sum() for f in clip.iter_frames(
                             fps=fps, dtype='uint32', progress_bar=1)]
    
    luminosities = np.array(luminosities, dtype=float)
    if clip is not None:
        end = clip.duration
    else:
        end = len(luminosities)*(1.0/fps) 
    lum_diffs = abs(np.diff(luminosities))
    avg = lum_diffs.mean()
    luminosity_jumps = 1+np.array(np.nonzero(lum_diffs> thr*avg))[0]
    tt = [0]+list((1.0/fps) *luminosity_jumps) + [end]
    #print tt
    cuts = [(t1,t2) for t1,t2 in zip(tt,tt[1:])]
    return cuts, luminosities
