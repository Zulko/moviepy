from moviepy import VideoFileClip
import math

my_clip = VideoFileClip("example.mp4")


def scroll(get_frame, t):
    """
    This function returns a 'region' of the current frame.
    The position of this region depends on the time.
    """
    frame = get_frame(t)
    frame_region = frame[int(t) : int(t) + 360, :]
    return frame_region


modified_clip1 = my_clip.transform(scroll)
