
import threading
import time
import pygame as pg
import numpy as np

from moviepy.decorators import (requires_duration, convert_masks_to_RGB)
from moviepy.tools import cvsecs


pg.init()
pg.display.set_caption('MoviePy')

def imdisplay(imarray, screen=None):
    """Splashes the given image array on the given pygame screen """
    a = pg.surfarray.make_surface(imarray.swapaxes(0, 1))
    if screen is None:
        screen = pg.display.set_mode(imarray.shape[:2][::-1])
    screen.blit(a, (0, 0))
    pg.display.flip()


@convert_masks_to_RGB
def show(clip, t=0, with_mask=True, interactive=False):
    """
    Splashes the frame of clip corresponding to time ``t``.
    
    Parameters
    ------------
    
    t
      Time in seconds of the frame to display.
    
    with_mask
      ``False`` if the clip has a mask but you want to see the clip
      without the mask.
    
    """

    if isinstance(t, tuple):
        t = cvsecs(*t)

    if with_mask and (clip.mask is not None):
        import moviepy.video.compositing.CompositeVideoClip as cvc
        clip = cvc.CompositeVideoClip([clip.set_pos((0,0))])
    img = clip.get_frame(t)
    imdisplay(img)

    if interactive:
        result=[]
        while True:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if (event.key == pg.K_ESCAPE):
                        print( "Keyboard interrupt" )
                        return result
                elif event.type == pg.MOUSEBUTTONDOWN:
                     x,y = pg.mouse.get_pos()
                     rgb = img[y,x]
                     result.append({'position':(x,y), 'color':rgb})
                     print( "position, color : ", "%s, %s"%(
                             str((x,y)),str(rgb)))
            time.sleep(.03)

@requires_duration
@convert_masks_to_RGB
def preview(clip, fps=15, audio=True, audio_fps=22050,
             audio_buffersize=3000, audio_nbytes=2):
    """ 
    Displays the clip in a window, at the given frames per second
    (of movie) rate. It will avoid that the clip be played faster
    than normal, but it cannot avoid the clip to be played slower
    than normal if the computations are complex. In this case, try
    reducing the ``fps``.
    
    Parameters
    ------------
    
    fps
      Number of frames per seconds in the displayed video.
        
    audio
      ``True`` (default) if you want the clip's audio be played during
      the preview.
        
    audiofps
      The frames per second to use when generating the audio sound.
      
    """
    
    import pygame as pg
    
    # compute and splash the first image
    screen = pg.display.set_mode(clip.size)
    
    audio = audio and (clip.audio is not None)
    
    if audio:
        # the sound will be played in parrallel. We are not
        # parralellizing it on different CPUs because it seems that
        # pygame and openCV already use several cpus it seems.
        
        # two synchro-flags to tell whether audio and video are ready
        videoFlag = threading.Event()
        audioFlag = threading.Event()
        # launch the thread
        audiothread = threading.Thread(target=clip.audio.preview,
            args = (audio_fps,audio_buffersize, audio_nbytes,
                    audioFlag, videoFlag))
        audiothread.start()
    
    img = clip.get_frame(0)
    imdisplay(img, screen)
    if audio: # synchronize with audio
        videoFlag.set() # say to the audio: video is ready
        audioFlag.wait() # wait for the audio to be ready
    
    result = []
    
    t0 = time.time()
    for t in np.arange(1.0 / fps, clip.duration-.001, 1.0 / fps):
        
        img = clip.get_frame(t)
        
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if (event.key == pg.K_ESCAPE):
                    
                    if audio:
                        videoFlag.clear()
                    print( "Keyboard interrupt" )
                    return result
                    
            elif event.type == pg.MOUSEBUTTONDOWN:
                x,y = pg.mouse.get_pos()
                rgb = img[y,x]
                result.append({'time':t, 'position':(x,y),
                                'color':rgb})
                print( "time, position, color : ", "%.03f, %s, %s"%(
                             t,str((x,y)),str(rgb)))
                    
        t1 = time.time()
        time.sleep(max(0, t - (t1-t0)) )
        imdisplay(img, screen)
