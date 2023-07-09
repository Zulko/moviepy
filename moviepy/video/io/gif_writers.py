"""MoviePy video GIFs writing."""

import proglog
from moviepy.decorators import requires_duration, use_clip_fps_by_default
import imageio

@requires_duration
@use_clip_fps_by_default
def write_gif_with_imageio(
    clip, filename, fps=None, loop=0, logger="bar"
):
    """
        Writes the gif with the Python library ImageIO (calls FreeImage).    
    """
    logger = proglog.default_bar_logger(logger)

    writer = imageio.save(filename, duration=1.0 / fps, loop=loop)
    logger(message="MoviePy - Building file %s with imageio." % filename)

    for frame in clip.iter_frames(fps=fps, logger=logger, dtype="uint8"):
        writer.append_data(frame)
