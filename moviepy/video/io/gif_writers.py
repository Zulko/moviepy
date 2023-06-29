"""MoviePy video GIFs writing."""

import proglog
from moviepy.decorators import requires_duration, use_clip_fps_by_default
import imageio

@requires_duration
@use_clip_fps_by_default
def write_gif_with_imageio(
    clip, filename, fps=None, opt=0, loop=0, colors=None, logger="bar"
):
    """
        Writes the gif with the Python library ImageIO (calls FreeImage).    
    """
    if colors is None:
        colors = 256
    logger = proglog.default_bar_logger(logger)

    quantizer = 0 if opt != 0 else "nq"

    writer = imageio.save(
        filename, duration=1.0 / fps, quantizer=quantizer, palettesize=colors, loop=loop
    )
    logger(message="MoviePy - Building file %s with imageio." % filename)

    for frame in clip.iter_frames(fps=fps, logger=logger, dtype="uint8"):
        writer.append_data(frame)
