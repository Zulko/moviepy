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


class FrameMatch:

    def __init__(self, t1, t2, distance):
        self.t1, self.t2, self.distance = t1, t2, distance
        self.time_span = t2-t1

    def __str__(self):
        return '(%.04f, %.04f, %.04f)'%(self.t1, self.t2, self.time_span)

    def __repr__(self):
        return '(%.04f, %.04f, %.04f)'%(self.t1, self.t2, self.time_span)

    def __iter__(self):
        return [self.t1, self.t2, self.distance].__iter__()


class FrameMatches(list):

    def __init__(self, lst):

        list.__init__(self, sorted(lst, key=lambda e: e.distance))

    def best(self, n=None, percent=None):
        if percent is not None:
            n = len(self)*percent/100
        return FrameMatches(self[:n])
    
    def filter(self, fun):
        return FrameMatches(filter(fun, self))

    def save(self, filename):
        np.savetxt(np.array(self), matching_frames, fmt='%.03f', delimiter='\t')

    @staticmethod
    def load(filename):
        arr = np.loadtxt(filename)
        mfs = [FrameMatch(*e) for e in arr]

        



def find_matching_frames(clip, dist_thr, max_d, fps=None):
    """ Returns a list [(t1, t2, distance), ...] for all pairs of frames with
    (t2-t1 < max_d). Optimized routine. Quite fast.

    clip : a MoviePy video clip, possibly transformed/resized
    dist_thr: distance above which a match is rejected
    max_d: maximal duration (in seconds) between two matching frames
    fps: frames per second (default will be clip.fps)
    """ 
    
    N_pixels = clip.w * clip.h * 3
    dot_product = lambda F1, F2: (F1*F2).sum()/N_pixels
    F = {} # will store the frames and their mutual distances
    
    def distance(t1, t2):
        uv = dot_product(F[t1]['frame'], F[t2]['frame'])
        u, v = F[t1]['|F|sq'], F[t2]['|F|sq']
        return np.sqrt(u+v - 2*uv)
    
    matching_frames = [] # the final result.
    
    for (t,frame) in clip.iter_frames(with_times=True, progress_bar=True):
        
        flat_frame = 1.0*frame.flatten()
        F_norm_sq = dot_product(flat_frame, flat_frame)
        F_norm = np.sqrt(F_norm_sq)
        
        for t2 in F.keys():
            # forget old frames, add 't' to the others frames
            # check for early rejections based on differing norms
            if (t-t2) > max_d:
                F.pop(t2)
            else:
                F[t2][t] = {'min':abs(F[t2]['|F|'] - F_norm),
                            'max':F[t2]['|F|'] + F_norm}
                F[t2][t]['rejected']= (F[t2][t]['min'] > dist_thr)
        
        t_F = sorted(F.keys())
        
        F[t] = {'frame': flat_frame, '|F|sq': F_norm_sq, '|F|': F_norm}
                
        for i,t2 in enumerate(t_F):
            # Compare F(t) to all the previous frames
            
            if F[t2][t]['rejected']:
                continue
            
            dist = distance(t, t2)
            F[t2][t]['min'] = F[t2][t]['max'] = dist
            F[t2][t]['rejected']  = (dist >= dist_thr)
            
            for t3 in t_F[i+1:]:
                # For all the next times t3, use d(F(t), F(t2)) to
                # update the bounds on d(F(t), F(t3)). See if you can
                # conclude on wether F(t) and F(t3) match.
                t3t, t2t3 = F[t3][t], F[t2][t3]
                t3t['max'] = min(t3t['max'], dist+ t2t3['max'])
                t3t['min'] = max(t3t['min'], dist - t2t3['max'],
                                 t2t3['min'] - dist)
                                      
                if t3t['min'] > dist_thr:
                    t3t['rejected'] = True
    
        # Store all the good matches (t2,t)
        matching_frames += [(t1, t, F[t1][t]['min']) for t1 in F
                            if (t1!=t) and not F[t1][t]['rejected']]
                   
    return FrameMatches([FrameMatch(*e) for e in matching_frames])



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
