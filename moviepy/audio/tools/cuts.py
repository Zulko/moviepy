
import numpy as np


def find_audio_period(aclip, t_min=.1, t_max=2, t_res=.01):
    """ Finds the period, in seconds of an audioclip.
    
    The beat is then given by bpm = 60/T

    t_min and _tmax are bounds for the returned value, t_res
    is the numerical precision
    """
    chunksize = int(t_res*aclip.fps)
    chunk_duration = 1.0*chunksize/aclip.fps
    # v denotes the list of volumes
    v = np.array([(c**2).sum() for c in
                aclip.iter_chunks(chunksize)])
    v = v-v.mean()
    corrs = np.correlate(v, v, mode = 'full')[-len(v):]
    corrs[:int(t_min/chunk_duration)]=0
    corrs[int(t_max/chunk_duration):]=0
    return chunk_duration*np.argmax(corrs)
