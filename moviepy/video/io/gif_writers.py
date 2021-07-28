"""MoviePy video GIFs writing."""

import os
import subprocess as sp

import numpy as np
import proglog

from moviepy.config import FFMPEG_BINARY, IMAGEMAGICK_BINARY
from moviepy.decorators import requires_duration, use_clip_fps_by_default
from moviepy.tools import cross_platform_popen_params, subprocess_call
from moviepy.video.fx.loop import loop as loop_fx


try:
    import imageio

    IMAGEIO_FOUND = True
except ImportError:
    IMAGEIO_FOUND = False


@requires_duration
@use_clip_fps_by_default
def write_gif_with_tempfiles(
    clip,
    filename,
    fps=None,
    program="ImageMagick",
    opt="OptimizeTransparency",
    fuzz=1,
    loop=0,
    dispose=True,
    colors=None,
    pixel_format=None,
    logger="bar",
):
    """Write the VideoClip to a GIF file.


    Converts a VideoClip into an animated GIF using ImageMagick
    or ffmpeg. Does the same as write_gif (see this one for more
    docstring), but writes every frame to a file instead of passing
    them in the RAM. Useful on computers with little RAM.

    Parameters
    ----------

    clip : moviepy.video.VideoClip.VideoClip
      The clip from which the frames will be extracted to create the GIF image.

    filename : str
      Name of the resulting gif file.

    fps : int, optional
      Number of frames per second. If it isn't provided, then the function will
      look for the clip's ``fps`` attribute.

    program : str, optional
      Software to use for the conversion, either ``"ImageMagick"`` or
      ``"ffmpeg"``.

    opt : str, optional
      ImageMagick only optimalization to apply, either ``"optimizeplus"`` or
      ``"OptimizeTransparency"``. Doesn't takes effect if ``program="ffmpeg"``.

    fuzz : float, optional
      ImageMagick only compression option which compresses the GIF by
      considering that the colors that are less than ``fuzz`` different are in
      fact the same.

    loop : int, optional
      Repeat the clip using ``loop`` iterations in the resulting GIF.

    dispose : bool, optional
      ImageMagick only option which, when enabled, the ImageMagick binary will
      take the argument `-dispose 2`, clearing the frame area with the
      background color, otherwise it will be defined as ``-dispose 1`` which
      will not dispose, just overlays next frame image.

    colors : int, optional
      ImageMagick only option for color reduction. Defines the maximum number
      of colors that the output image will have.

    pixel_format : str, optional
      FFmpeg pixel format for the output gif file. If is not specified
      ``"rgb24"`` will be used as the default format unless ``clip.mask``
      exist, then ``"rgba"`` will be used. Doesn't takes effect if
      ``program="ImageMagick"``.

    logger : str, optional
      Either ``"bar"`` for progress bar or ``None`` or any Proglog logger.
    """
    logger = proglog.default_bar_logger(logger)
    file_root, ext = os.path.splitext(filename)
    tt = np.arange(0, clip.duration, 1.0 / fps)

    tempfiles = []

    logger(message="MoviePy - Building file %s\n" % filename)
    logger(message="MoviePy - - Generating GIF frames")

    for i, t in logger.iter_bar(t=list(enumerate(tt))):

        name = "%s_GIFTEMP%04d.png" % (file_root, i + 1)
        tempfiles.append(name)
        clip.save_frame(name, t, with_mask=True)

    delay = int(100.0 / fps)

    if clip.mask is None:
        with_mask = False

    if program == "ImageMagick":
        if not pixel_format:
            pixel_format = "RGBA" if with_mask else "RGB"

        logger(message="MoviePy - - Optimizing GIF with ImageMagick...")
        cmd = (
            [
                IMAGEMAGICK_BINARY,
                "-delay",
                "%d" % delay,
                "-dispose",
                "%d" % (2 if dispose else 1),
                "-loop",
                "%d" % loop,
                "%s_GIFTEMP*.png" % file_root,
                "-coalesce",
                "-fuzz",
                "%02d" % fuzz + "%",
                "-layers",
                "%s" % opt,
                "-set",
                "colorspace",
                pixel_format,
            ]
            + (["-colors", "%d" % colors] if colors is not None else [])
            + [filename]
        )

    elif program == "ffmpeg":
        if loop:
            clip = loop_fx(clip, n=loop)

        if not pixel_format:
            pixel_format = "rgba" if with_mask else "rgb24"

        cmd = [
            FFMPEG_BINARY,
            "-y",
            "-f",
            "image2",
            "-r",
            str(fps),
            "-i",
            file_root + "_GIFTEMP%04d.png",
            "-r",
            str(fps),
            filename,
            "-pix_fmt",
            (pixel_format),
        ]

    try:
        subprocess_call(cmd, logger=logger)
        logger(message="MoviePy - GIF ready: %s." % filename)

    except (IOError, OSError) as err:

        error = (
            "MoviePy Error: creation of %s failed because "
            "of the following error:\n\n%s.\n\n." % (filename, str(err))
        )

        if program == "ImageMagick":
            error += (
                "This error can be due to the fact that "
                "ImageMagick is not installed on your computer, or "
                "(for Windows users) that you didn't specify the "
                "path to the ImageMagick binary. Check the documentation."
            )

        raise IOError(error)

    for file in tempfiles:
        os.remove(file)


@requires_duration
@use_clip_fps_by_default
def write_gif(
    clip,
    filename,
    fps=None,
    with_mask=True,
    program="ImageMagick",
    opt="OptimizeTransparency",
    fuzz=1,
    loop=0,
    dispose=True,
    colors=None,
    pixel_format=None,
    logger="bar",
):
    """Write the VideoClip to a GIF file, without temporary files.

    Converts a VideoClip into an animated GIF using ImageMagick
    or ffmpeg.


    Parameters
    ----------

    clip : moviepy.video.VideoClip.VideoClip
      The clip from which the frames will be extracted to create the GIF image.

    filename : str
      Name of the resulting gif file.

    fps : int, optional
      Number of frames per second. If it isn't provided, then the function will
      look for the clip's ``fps`` attribute.

    with_mask : bool, optional
      Includes the mask of the clip in the output (the clip must have a mask
      if this argument is ``True``).

    program : str, optional
      Software to use for the conversion, either ``"ImageMagick"`` or
      ``"ffmpeg"``.

    opt : str, optional
      ImageMagick only optimalization to apply, either ``"optimizeplus"`` or
      ``"OptimizeTransparency"``. Doesn't takes effect if ``program="ffmpeg"``.

    fuzz : float, optional
      ImageMagick only compression option which compresses the GIF by
      considering that the colors that are less than ``fuzz`` different are in
      fact the same.

    loop : int, optional
      Repeat the clip using ``loop`` iterations in the resulting GIF.

    dispose : bool, optional
      ImageMagick only option which, when enabled, the ImageMagick binary will
      take the argument `-dispose 2`, clearing the frame area with the
      background color, otherwise it will be defined as ``-dispose 1`` which
      will not dispose, just overlays next frame image.

    colors : int, optional
      ImageMagick only option for color reduction. Defines the maximum number
      of colors that the output image will have.

    pixel_format : str, optional
      FFmpeg pixel format for the output gif file. If is not specified
      ``"rgb24"`` will be used as the default format unless ``clip.mask``
      exist, then ``"rgba"`` will be used. Doesn't takes effect if
      ``program="ImageMagick"``.

    logger : str, optional
      Either ``"bar"`` for progress bar or ``None`` or any Proglog logger.


    Examples
    --------

    The gif will be playing the clip in real time, you can only change the
    frame rate. If you want the gif to be played slower than the clip you will
    use:

    >>> # slow down clip 50% and make it a GIF
    >>> myClip.multiply_speed(0.5).write_gif('myClip.gif')
    """
    #
    # We use processes chained with pipes.
    #
    # if program == 'ffmpeg'
    # frames --ffmpeg--> gif
    #
    # if program == 'ImageMagick' and optimize == (None, False)
    # frames --ffmpeg--> bmp frames --ImageMagick--> gif
    #
    #
    # if program == 'ImageMagick' and optimize != (None, False)
    # frames -ffmpeg-> bmp frames -ImagMag-> gif -ImagMag-> better gif
    #

    delay = 100.0 / fps
    logger = proglog.default_bar_logger(logger)
    if clip.mask is None:
        with_mask = False
    if not pixel_format:
        pixel_format = "rgba" if with_mask else "rgb24"

    cmd1 = [
        FFMPEG_BINARY,
        "-y",
        "-loglevel",
        "error",
        "-f",
        "rawvideo",
        "-vcodec",
        "rawvideo",
        "-r",
        "%.02f" % fps,
        "-s",
        "%dx%d" % (clip.w, clip.h),
        "-pix_fmt",
        (pixel_format),
        "-i",
        "-",
    ]

    popen_params = cross_platform_popen_params(
        {"stdout": sp.DEVNULL, "stderr": sp.DEVNULL, "stdin": sp.DEVNULL}
    )

    if program == "ffmpeg":
        if loop:
            clip = loop_fx(clip, n=loop)

        popen_params["stdin"] = sp.PIPE
        popen_params["stdout"] = sp.DEVNULL

        proc1 = sp.Popen(
            cmd1
            + [
                "-pix_fmt",
                (pixel_format),
                "-r",
                "%.02f" % fps,
                filename,
            ],
            **popen_params,
        )
    else:

        popen_params["stdin"] = sp.PIPE
        popen_params["stdout"] = sp.PIPE

        proc1 = sp.Popen(
            cmd1 + ["-f", "image2pipe", "-vcodec", "bmp", "-"], **popen_params
        )

    if program == "ImageMagick":

        cmd2 = [
            IMAGEMAGICK_BINARY,
            "-delay",
            "%.02f" % (delay),
            "-dispose",
            "%d" % (2 if dispose else 1),
            "-loop",
            "%d" % loop,
            "-",
            "-coalesce",
        ]

        if opt in [False, None]:
            popen_params["stdin"] = proc1.stdout
            popen_params["stdout"] = sp.DEVNULL
            proc2 = sp.Popen(cmd2 + [filename], **popen_params)

        else:
            popen_params["stdin"] = proc1.stdout
            popen_params["stdout"] = sp.PIPE
            proc2 = sp.Popen(cmd2 + ["gif:-"], **popen_params)

        if opt:

            cmd3 = (
                [
                    IMAGEMAGICK_BINARY,
                    "-",
                    "-fuzz",
                    "%d" % fuzz + "%",
                    "-layers",
                    opt,
                ]
                + (["-colors", "%d" % colors] if colors is not None else [])
                + [filename]
            )

            popen_params["stdin"] = proc2.stdout
            popen_params["stdout"] = sp.DEVNULL
            proc3 = sp.Popen(cmd3, **popen_params)

    # We send all the frames to the first process
    logger(message="MoviePy - Building file  %s" % filename)
    logger(message="MoviePy - - Generating GIF frames.")
    try:
        for t, frame in clip.iter_frames(
            fps=fps, logger=logger, with_times=True, dtype="uint8"
        ):
            if with_mask:
                mask = 255 * clip.mask.get_frame(t)
                frame = np.dstack([frame, mask]).astype("uint8")
            proc1.stdin.write(frame.tobytes())

    except IOError as err:

        error = (
            "[MoviePy] Error: creation of %s failed because "
            "of the following error:\n\n%s.\n\n." % (filename, str(err))
        )

        if program == "ImageMagick":
            error += (
                "This can be due to the fact that "
                "ImageMagick is not installed on your computer, or "
                "(for Windows users) that you didn't specify the "
                "path to the ImageMagick binary. Check the documentation."
            )

        raise IOError(error)
    if program == "ImageMagick":
        logger(message="MoviePy - - Optimizing GIF with ImageMagick.")
    proc1.stdin.close()
    proc1.wait()
    if program == "ImageMagick":
        proc2.wait()
        if opt:
            proc3.wait()
    logger(message="MoviePy - - File ready: %s." % filename)


def write_gif_with_image_io(
    clip, filename, fps=None, opt=0, loop=0, colors=None, logger="bar"
):
    """Writes the gif with the Python library ImageIO (calls FreeImage)."""
    if colors is None:
        colors = 256
    logger = proglog.default_bar_logger(logger)

    if not IMAGEIO_FOUND:
        raise ImportError(
            "Writing a gif with imageio requires ImageIO installed,"
            " with e.g. 'pip install imageio'"
        )

    if fps is None:
        fps = clip.fps

    quantizer = 0 if opt != 0 else "nq"

    writer = imageio.save(
        filename, duration=1.0 / fps, quantizer=quantizer, palettesize=colors, loop=loop
    )
    logger(message="MoviePy - Building file %s with imageio." % filename)

    for frame in clip.iter_frames(fps=fps, logger=logger, dtype="uint8"):

        writer.append_data(frame)
