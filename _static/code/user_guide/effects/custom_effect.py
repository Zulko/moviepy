"""Let's write a custom effect that will add a basic progress bar
at the bottom of our clip."""

from moviepy import VideoClip
from moviepy.decorators import requires_duration


# Here you see a decorator that will verify if our clip have a duration
# MoviePy offer a few of them that may come handy when writing your own effects
@requires_duration
def progress_bar(clip: VideoClip, color: tuple, height: int = 10):
    """
    Add a progress bar at the bottom of our clip

     Parameters
    ----------

      color: Color of the bar as a RGB tuple
      height: The height of the bar in pixels. Default = 10
    """

    # Because we have define the filter func inside our global effect,
    # it have access to global effect scope and can use clip from inside filter
    def filter(get_frame, t):
        progression = t / clip.duration
        bar_width = int(progression * clip.w)

        # Showing a progress bar is just replacing bottom pixels
        # on some part of our frame
        frame = get_frame(t)
        frame[-height:, 0:bar_width] = color

        return frame

    return clip.transform(filter, apply_to="mask")
