"""Cutting utilities working with audio."""

from typing import TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from moviepy.audio.AudioClip import AudioClip


def find_audio_period(
    clip: AudioClip,
    min_time: float = 0.1,
    max_time: float = 2,
    time_resolution: float = 0.01,
):
    """Finds the period, in seconds of an audioclip.

    Parameters
    ----------

    min_time : float, optional
      Minimum bound for the returned value.

    max_time : float, optional
      Maximum bound for the returned value.

    time_resolution : float, optional
      Numerical precision.
    """
    chunksize = int(time_resolution * clip.fps)
    chunk_duration = 1.0 * chunksize / clip.fps
    # v denotes the list of volumes
    v = np.array([(chunk**2).sum() for chunk in clip.iter_chunks(chunksize)])
    v = v - v.mean()
    corrs = np.correlate(v, v, mode="full")[-len(v) :]
    corrs[: int(min_time / chunk_duration)] = 0
    corrs[int(max_time / chunk_duration) :] = 0
    return chunk_duration * np.argmax(corrs)
