"""MoviePy video GIFs writing."""

import imageio.v3 as iio
import numpy as np
import proglog

from moviepy.decorators import requires_duration, use_clip_fps_by_default


@requires_duration
@use_clip_fps_by_default
def write_gif_with_imageio(clip, filename, fps=None, loop=0, logger="bar"):
    """Writes the gif with the Python library ImageIO (calls FreeImage)."""
    logger = proglog.default_bar_logger(logger)

    # Optional GPU compositor: keep compositing on GPU (CuPy) and download
    # only at the ImageIO boundary.
    try:
        from moviepy.video.tools import gpu_render
    except Exception:
        gpu_render = None

    with iio.imopen(filename, "w", plugin="pillow") as writer:
        logger(message="MoviePy - Building file %s with imageio." % filename)
        if (
            (gpu_render is not None)
            and gpu_render.is_enabled()
            and gpu_render.is_available()
        ):
            # Match Clip.iter_frames() time arithmetic for compatibility.
            n_frames = int(clip.duration * fps)
            for frame_index in logger.iter_bar(frame_index=range(n_frames)):
                t = np.float64(frame_index) / fps
                # GIF writing does not support full alpha semantics; keep RGB.
                frame = gpu_render._composite_rgb_gpu(clip, t)
                if hasattr(frame, "__cuda_array_interface__"):
                    try:
                        import cupy as cp

                        frame = cp.asnumpy(frame)
                    except Exception:
                        pass
                writer.write(frame, duration=1000 / fps, loop=loop)
        else:
            for frame in clip.iter_frames(fps=fps, logger=logger, dtype="uint8"):
                if hasattr(frame, "__cuda_array_interface__"):
                    try:
                        import cupy as cp

                        frame = cp.asnumpy(frame)
                    except Exception:
                        pass
                writer.write(
                    frame, duration=1000 / fps, loop=loop
                )  # Duration is in ms not s
