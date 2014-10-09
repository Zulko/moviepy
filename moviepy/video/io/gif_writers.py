import os
import subprocess as sp
from tqdm import tqdm
from moviepy.config import get_setting
from moviepy.decorators import requires_duration
from moviepy.tools import verbose_print, subprocess_call
import numpy as np

try:
    from subprocess import DEVNULL  # py3k
except ImportError:
    DEVNULL = open(os.devnull, 'wb')


@requires_duration
def write_gif_with_tempfiles(clip, filename, fps=None, program= 'ImageMagick',
       opt="OptimizeTransparency", fuzz=1, verbose=True,
       loop=0, dispose=False, colors=None, tempfiles=False):
    """ Write the VideoClip to a GIF file.


    Converts a VideoClip into an animated GIF using ImageMagick
    or ffmpeg. Does the same as write_gif (see this one for more
    docstring), but writes every frame to a file instead of passing
    them in the RAM. Useful on computers with little RAM.

    """

    if fps is None:
        fps = clip.fps

    fileName, fileExtension = os.path.splitext(filename)
    tt = np.arange(0,clip.duration, 1.0/fps)

    tempfiles = []

    verbose_print(verbose, "\nMoviePy: building GIF file %s\n"%filename
                  +40*"-"+"\n")

    verbose_print(verbose, "Generating GIF frames.\n")

    total = int(clip.duration*fps)+1
    for i, t in tqdm(enumerate(tt), total=total):

        name = "%s_GIFTEMP%04d.png"%(fileName, i+1)
        tempfiles.append(name)
        clip.save_frame(name, t, savemask=True)

    verbose_print(verbose, "Done generating GIF frames.\n")

    delay = int(100.0/fps)

    if program == "ImageMagick":

        cmd = [get_setting("IMAGEMAGICK_BINARY"),
              '-delay' , '%d'%delay,
              "-dispose" ,"%d"%(2 if dispose else 1),
              "-loop" , "%d"%loop,
              "%s_GIFTEMP*.png"%fileName,
              "-coalesce",
              "-layers", "%s"%opt,
              "-fuzz", "%02d"%fuzz + "%",
              ]+(["-colors", "%d"%colors] if colors is not None else [])+[
              filename]

    elif program == "ffmpeg":

        cmd = [get_setting("FFMPEG_BINARY"), '-y',
               '-f', 'image2', '-r',str(fps),
               '-i', fileName+'_GIFTEMP%04d.png',
               '-r',str(fps),
               filename]

    try:
        subprocess_call( cmd, verbose = verbose )

    except (IOError,OSError) as err:

        error = ("MoviePy Error: creation of %s failed because "
          "of the following error:\n\n%s.\n\n."%(filename, str(err)))

        if program == "ImageMagick":
            error = error + ("This error can be due to the fact that "
                "ImageMagick is not installed on your computer, or "
                "(for Windows users) that you didn't specify the "
                "path to the ImageMagick binary in file conf.py." )

        raise IOError(error)

    for f in tempfiles:
        os.remove(f)



@requires_duration
def write_gif(clip, filename, fps=None, program= 'ImageMagick',
           opt="OptimizeTransparency", fuzz=1, verbose=True,
           loop=0, dispose=False, colors=None):
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

    if fps is None:
        fps=clip.fps
    delay= 100.0/fps

    cmd1 = [get_setting("FFMPEG_BINARY"), '-y', '-loglevel', 'error',
            '-f', 'rawvideo',
            '-vcodec','rawvideo', '-r', "%.02f"%fps,
            '-s', "%dx%d"%(clip.w, clip.h), '-pix_fmt', 'rgb24',
            '-i', '-']

    popen_params = {"stdout": DEVNULL,
                    "stderr": DEVNULL,
                    "stdin": DEVNULL}

    if os.name == "nt":
        popen_params["creationflags"] = 0x08000000

    if program == "ffmpeg":
        popen_params["stdin"] = sp.PIPE
        popen_params["stdout"] = DEVNULL

        proc1 = sp.Popen(cmd1+['-r', "%.02f"%fps, filename], **popen_params)
    else:

        popen_params["stdin"] = sp.PIPE
        popen_params["stdout"] = sp.PIPE

        proc1 = sp.Popen(cmd1+['-f', 'image2pipe',
                               '-vcodec', 'bmp', '-'],
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

            cmd3 = [get_setting("IMAGEMAGICK_BINARY"), '-', '-layers', opt,
                    '-fuzz', '%d'%fuzz+'%'
                   ]+(["-colors", "%d"%colors] if colors is not None else [])+[
                   filename]

            popen_params["stdin"] = proc2.stdout
            popen_params["stdout"] = DEVNULL
            proc3 = sp.Popen(cmd3, **popen_params)

    # We send all the frames to the first process
    verbose_print(verbose, "\nMoviePy: building GIF file %s\n"%filename
                            +40*"-"+"\n")
    verbose_print(verbose, "Generating GIF frames...\n")

    try:

        for frame in clip.iter_frames(fps=fps, progress_bar=True):
            proc1.stdin.write(frame.tostring())
        verbose_print(verbose, "Done.\n")

    except IOError as err:

        error = ("MoviePy Error: creation of %s failed because "
          "of the following error:\n\n%s.\n\n."%(filename, str(err)))

        if program == "ImageMagick":
            error = error + ("This can be due to the fact that "
                "ImageMagick is not installed on your computer, or "
                "(for Windows users) that you didn't specify the "
                "path to the ImageMagick binary in file conf.py." )

        raise IOError(error)
    verbose_print(verbose, "Writing GIF... ")
    proc1.stdin.close()
    proc1.wait()
    if program == 'ImageMagick':
        proc2.wait()
        if opt:
            proc3.wait()
    verbose_print(verbose, 'Done. Your GIF is ready !')