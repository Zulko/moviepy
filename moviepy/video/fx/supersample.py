import numpy as np


def supersample(clip, d, n_frames):
    """Replaces each frame at time t by the mean of `n_frames` equally spaced frames
    taken in the interval [t-d, t+d]. This results in motion blur.
    """

    def filter(get_frame, t):
        timings = np.linspace(t - d, t + d, n_frames)
        frame_average = np.mean(
            1.0 * np.array([get_frame(t_) for t_ in timings], dtype="uint16"), axis=0
        )
        return frame_average.astype("uint8")

    return clip.transform(filter)
