"""MoviePy video GIFs writing."""

import imageio.v3 as iio
import proglog

from moviepy.decorators import requires_duration, use_clip_fps_by_default


@requires_duration
@use_clip_fps_by_default
def write_gif_with_imageio(clip, filename, fps=None, loop=0, logger="bar"):
    """Writes the gif with the Python library ImageIO (calls FreeImage)."""
    logger = proglog.default_bar_logger(logger)

    with iio.imopen(filename, "w", plugin="pillow") as writer:
        logger(message="MoviePy - Building file %s with imageio." % filename)
        for frame in clip.iter_frames(fps=fps, logger=logger, dtype="uint8"):
            writer.write(
                frame, duration=1000 / fps, loop=loop
            )  # Duration is in ms not s
