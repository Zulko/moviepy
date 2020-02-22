import os
import subprocess as sp

import numpy as np
import proglog

from moviepy.compat import DEVNULL
from moviepy.config import get_setting
from moviepy.decorators import requires_duration, use_clip_fps_by_default
from moviepy.tools import subprocess_call

try:
    import imageio
    IMAGEIO_FOUND = True
except ImportError:
    IMAGEIO_FOUND = False


@requires_duration
@use_clip_fps_by_default
def write_gif_with_tempfiles(clip, filename, fps=None, program= 'ImageMagick',
       opt="OptimizeTransparency", fuzz=1, verbose=True,
       loop=0, dispose=True, colors=None, logger='bar'):
    """ Write the VideoClip to a GIF file.


    Converts a VideoClip into an animated GIF using ImageMagick
    or ffmpeg. Does the same as write_gif (see this one for more
    docstring), but writes every frame to a file instead of passing
    them in the RAM. Useful on computers with little RAM.

    """
    logger = proglog.default_bar_logger(logger)
    fileName, ext = os.path.splitext(filename)
    tt = np.arange(0,clip.duration, 1.0/fps)

    tempfiles = []
    
    logger(message='MoviePy - Building file %s\n' % filename)
    logger(message='MoviePy - - Generating GIF frames')

    
    for i, t in logger.iter_bar(t=list(enumerate(tt))):

        name = "%s_GIFTEMP%04d.png"%(fileName, i+1)
        tempfiles.append(name)
        clip.save_frame(name, t, withmask=True)

    delay = int(100.0/fps)

    if program == "ImageMagick":
        logger(message='MoviePy - - Optimizing GIF with ImageMagick...')
        cmd = [get_setting("IMAGEMAGICK_BINARY"),
              '-delay' , '%d'%delay,
              "-dispose" ,"%d"%(2 if dispose else 1),
              "-loop" , "%d"%loop,
              "%s_GIFTEMP*.png"%fileName,
              "-coalesce",
              "-fuzz", "%02d"%fuzz + "%",
              "-layers", "%s"%opt,
              ]+(["-colors", "%d"%colors] if colors is not None else [])+[
              filename]

    elif program == "ffmpeg":

        cmd = [get_setting("FFMPEG_BINARY"), '-y',
               '-f', 'image2', '-r',str(fps),
               '-i', fileName+'_GIFTEMP%04d.png',
               '-r',str(fps),
               filename]

    try:
        subprocess_call(cmd, logger=logger)
        logger(message='MoviePy - GIF ready: %s.' % filename)

    except (IOError,OSError) as err:

        error = ("MoviePy Error: creation of %s failed because "
          "of the following error:\n\n%s.\n\n."%(filename, str(err)))

        if program == "ImageMagick":
            error = error + ("This error can be due to the fact that "
                "ImageMagick is not installed on your computer, or "
                "(for Windows users) that you didn't specify the "
                "path to the ImageMagick binary in file config_defaults.py." )

        raise IOError(error)

    for f in tempfiles:
        os.remove(f)



@requires_duration
@use_clip_fps_by_default
def write_gif(clip, filename, fps=None, program= 'ImageMagick',
           opt="OptimizeTransparency", fuzz=1, verbose=True, withmask=True,
           loop=0, dispose=True, colors=None, logger='bar'):
    """ Write the VideoClip to a GIF file, without temporary files.

    Converts a VideoClip into an animated GIF using ImageMagick
    or ffmpeg.


    Parameters
    -----------

    filename
      Name of the resulting gif file.

    fps
      Number of frames per second (see note below). If it
        isn't provided, then the function will look for the clip's
        ``fps`` attribute (VideoFileClip, for instance, have one).

    program
      Software to use for the conversion, either 'ImageMagick' or
      'ffmpeg'.

    opt
      (ImageMagick only) optimalization to apply, either
      'optimizeplus' or 'OptimizeTransparency'.

    fuzz
      (ImageMagick only) Compresses the GIF by considering that
      the colors that are less than fuzz% different are in fact
      the same.


    Notes
    -----

    The gif will be playing the clip in real time (you can
    only change the frame rate). If you want the gif to be played
    slower than the clip you will use ::

        >>> # slow down clip 50% and make it a gif
        >>> myClip.speedx(0.5).write_gif('myClip.gif')

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

    delay= 100.0/fps
    logger = proglog.default_bar_logger(logger)
    if clip.mask is None:
        withmask = False

    cmd1 = [get_setting("FFMPEG_BINARY"), '-y', '-loglevel', 'error',
            '-f', 'rawvideo',
            '-vcodec','rawvideo', '-r', "%.02f"%fps,
            '-s', "%dx%d"%(clip.w, clip.h),
            '-pix_fmt', ('rgba' if withmask else 'rgb24'),
            '-i', '-']

    popen_params = {"stdout": DEVNULL,
                    "stderr": DEVNULL,
                    "stdin": DEVNULL}

    if os.name == "nt":
        popen_params["creationflags"] = 0x08000000

    if program == "ffmpeg":
        popen_params["stdin"] = sp.PIPE
        popen_params["stdout"] = DEVNULL

        proc1 = sp.Popen(cmd1+[ '-pix_fmt', ('rgba' if withmask else 'rgb24'),
                                '-r', "%.02f"%fps, filename], **popen_params)
    else:

        popen_params["stdin"] = sp.PIPE
        popen_params["stdout"] = sp.PIPE

        proc1 = sp.Popen(cmd1+ ['-f', 'image2pipe', '-vcodec', 'bmp', '-'],
                         **popen_params)

    if program == 'ImageMagick':

        cmd2 = [get_setting("IMAGEMAGICK_BINARY"), '-delay', "%.02f"%(delay),
                "-dispose" ,"%d"%(2 if dispose else 1),
                '-loop', '%d'%loop, '-', '-coalesce']

        if (opt in [False, None]):
            popen_params["stdin"] = proc1.stdout
            popen_params["stdout"] = DEVNULL
            proc2 = sp.Popen(cmd2+[filename], **popen_params)

        else:
            popen_params["stdin"] = proc1.stdout
            popen_params["stdout"] = sp.PIPE
            proc2 = sp.Popen(cmd2+['gif:-'], **popen_params)

        if opt:

            cmd3 = [get_setting("IMAGEMAGICK_BINARY"), '-',
                    '-fuzz', '%d'%fuzz+'%', '-layers', opt
                   ]+(["-colors", "%d"%colors] if colors is not None else [])+[
                   filename]

            popen_params["stdin"] = proc2.stdout
            popen_params["stdout"] = DEVNULL
            proc3 = sp.Popen(cmd3, **popen_params)

    # We send all the frames to the first process
    logger(message='MoviePy - Building file  %s' % filename)
    logger(message='MoviePy - - Generating GIF frames.')
    try:
        for t,frame in clip.iter_frames(fps=fps, logger=logger,
                                        with_times=True,  dtype="uint8"):
            if withmask:
                mask = 255 * clip.mask.get_frame(t)
                frame = np.dstack([frame, mask]).astype('uint8')
            proc1.stdin.write(frame.tostring())

    except IOError as err:

        error = ("[MoviePy] Error: creation of %s failed because "
          "of the following error:\n\n%s.\n\n."%(filename, str(err)))

        if program == "ImageMagick":
            error = error + ("This can be due to the fact that "
                "ImageMagick is not installed on your computer, or "
                "(for Windows users) that you didn't specify the "
                "path to the ImageMagick binary in file config_defaults.py." )

        raise IOError(error)
    if program == 'ImageMagick':
        logger(message='MoviePy - - Optimizing GIF with ImageMagick.')
    proc1.stdin.close()
    proc1.wait()
    if program == 'ImageMagick':
        proc2.wait()
        if opt:
            proc3.wait()
    logger(message='MoviePy - - File ready: %s.' % filename)


def write_gif_with_image_io(clip, filename, fps=None, opt=0, loop=0,
                            colors=None, verbose=True, logger='bar'):
    """
    Writes the gif with the Python library ImageIO (calls FreeImage).

    Parameters
    -----------
    opt

    """

    if colors is None:
        colors = 256
    logger = proglog.default_bar_logger(logger)

    if not IMAGEIO_FOUND:
        raise ImportError("Writing a gif with imageio requires ImageIO installed,"
                         " with e.g. 'pip install imageio'")

    if fps is None:
        fps = clip.fps

    quantizer = 0 if opt != 0 else 'nq'

    writer = imageio.save(
        filename,
        duration=1.0/fps,
        quantizer=quantizer,
        palettesize=colors,
        loop=loop
        )
    logger(message='MoviePy - Building file %s with imageio.' % filename)

    for frame in clip.iter_frames(fps=fps, logger=logger, dtype='uint8'):

        writer.append_data(frame)
