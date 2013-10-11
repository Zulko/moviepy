import time
import numpy as np
import threading
import sys

import numpy as np

from moviepy.decorators import requires_duration
import pygame as pg

pg.init()
pg.display.set_caption('MoviePy')


@requires_duration
def preview(clip, fps=22050,  buffersize=50000, nbytes= 2,
                 audioFlag=None, videoFlag=None):
    """
    Plays the sound clip with pygame.
    
    :param fps: frame rate of the sound. 44100 gives top quality, but
        may cause problems if your computer is not fast enough and
        your clip is complicated. If the sound jumps during the
        preview lower it (11025 is still fine, 5000 is tolerable).
        
    :param buffersize: The sound is not generated all at once, but
        rather made by bunches of frames (chunks). ``buffersize``
        is the size of such a chunk. Try varying it if you meet
        audio problems (but you shouldn't have to).
    
    :param nbytes: number of bytes to encode the sound: 1 for 8bit
        sound, 2 for 16bit, 4 for 32bit sound. 2 bytes is fine.
    
    :param audioFlag, videoFlag: parameters whose sole purpose is to
        enable a good synchronization of the start of video and sound
        when the audio clip is played as the background of a video
        clip. ``audioFlag`` and ``videoFlag`` are threading.Event
        objects (from Python's standard threading module).
    """
                 
    pg.mixer.quit()
    
    pg.mixer.init(fps, -8 * nbytes, clip.nchannels, 1024)
    totalsize = int(fps*clip.duration)
    pospos = np.array(list(range(0, totalsize,  buffersize))+[totalsize])
    tt = (1.0/fps)*np.arange(pospos[0],pospos[1])
    sndarray = clip.to_soundarray(tt,nbytes)
    chunk = pg.sndarray.make_sound(sndarray)
    Delta = tt[1]-tt[0]
    
    if (audioFlag !=None) and (videoFlag!= None):
        audioFlag.set()
        videoFlag.wait()
        
    channel = chunk.play()
    for i in range(1,len(pospos)-1):
        tt = (1.0/fps)*np.arange(pospos[i],pospos[i+1])
        sndarray = clip.to_soundarray(tt,nbytes)
        chunk = pg.sndarray.make_sound(sndarray)
        while channel.get_queue():
            time.sleep(0.003)
            if (videoFlag!= None):
                if not videoFlag.is_set():
                    channel.stop()
                    del channel
                    return
        channel.queue(chunk)
