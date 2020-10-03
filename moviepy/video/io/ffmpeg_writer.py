"""
On the long term this will implement several methods to make videos
out of VideoClips
"""

import os
import subprocess as sp

import numpy as np
from proglog import proglog

from moviepy.config import FFMPEG_BINARY


class FFMPEG_VideoWriter:
    """A class for FFMPEG-based video writing.

    A class to write videos using ffmpeg. ffmpeg will write in a large
    choice of formats.

    Parameters
    -----------

    filename
      Any filename like 'video.mp4' etc. but if you want to avoid
      complications it is recommended to use the generic extension
      '.avi' for all your videos.

    size
      Size (width,height) of the output video in pixels.

    fps
      Frames per second in the output video file.

    codec
      FFMPEG codec. It seems that in terms of quality the hierarchy is
      'rawvideo' = 'png' > 'mpeg4' > 'libx264'
      'png' manages the same lossless quality as 'rawvideo' but yields
      smaller files. Type ``ffmpeg -codecs`` in a terminal to get a list
      of accepted codecs.

      Note for default 'libx264': by default the pixel format yuv420p
      is used. If the video dimensions are not both even (e.g. 720x405)
      another pixel format is used, and this can cause problem in some
      video readers.

    audiofile
      Optional: The name of an audio file that will be incorporated
      to the video.

    preset
      Sets the time that FFMPEG will take to compress the video. The slower,
      the better the compression rate. Possibilities are: ultrafast,superfast,
      veryfast, faster, fast, medium (default), slow, slower, veryslow,
      placebo.

    bitrate
      Only relevant for codecs which accept a bitrate. "5000k" offers
      nice results in general.

    withmask
      Boolean. Set to ``True`` if there is a mask in the video to be
      encoded.

    pix_fmt
      Optional: Pixel format for the output video file. If is not specified
      'rgb24' will be used as the default format unless ``withmask`` is set
      as ``True``, then 'rgba' will be used.

    """

    def __init__(
        self,
        filename,
        size,
        fps,
        codec="libx264",
        audiofile=None,
        preset="medium",
        bitrate=None,
        withmask=False,
        logfile=None,
        threads=None,
        ffmpeg_params=None,
        pix_fmt=None,
    ):
        if logfile is None:
            logfile = sp.PIPE
        self.logfile = logfile
        self.filename = filename
        self.codec = codec
        self.ext = self.filename.split(".")[-1]
        if not pix_fmt:
            pix_fmt = "rgba" if withmask else "rgb24"

        # order is important
        cmd = [
            FFMPEG_BINARY,
            "-y",
            "-loglevel",
            "error" if logfile == sp.PIPE else "info",
            "-f",
            "rawvideo",
            "-vcodec",
            "rawvideo",
            "-s",
            "%dx%d" % (size[0], size[1]),
            "-pix_fmt",
            pix_fmt,
            "-r",
            "%.02f" % fps,
            "-an",
            "-i",
            "-",
        ]
        if audiofile is not None:
            cmd.extend(["-i", audiofile, "-acodec", "copy"])
        cmd.extend(["-vcodec", codec, "-preset", preset])
        if ffmpeg_params is not None:
            cmd.extend(ffmpeg_params)
        if bitrate is not None:
            cmd.extend(["-b", bitrate])

        if threads is not None:
            cmd.extend(["-threads", str(threads)])

        if (codec == "libx264") and (size[0] % 2 == 0) and (size[1] % 2 == 0):
            cmd.extend(["-pix_fmt", "yuv420p"])
        cmd.extend([filename])

        popen_params = {"stdout": sp.DEVNULL, "stderr": logfile, "stdin": sp.PIPE}

        # This was added so that no extra unwanted window opens on windows
        # when the child process is created
        if os.name == "nt":
            popen_params["creationflags"] = 0x08000000  # CREATE_NO_WINDOW

        self.proc = sp.Popen(cmd, **popen_params)

    def write_frame(self, img_array):
        """ Writes one frame in the file."""
        try:
            self.proc.stdin.write(img_array.tobytes())
        except IOError as err:
            _, ffmpeg_error = self.proc.communicate()
            if ffmpeg_error is not None:
                ffmpeg_error = ffmpeg_error.decode()
            else:
                # The error was redirected to a logfile with `write_logfile=True`,
                # so read the error from that file instead
                self.logfile.seek(0)
                ffmpeg_error = self.logfile.read()

            error = (
                f"{err}\n\nMoviePy error: FFMPEG encountered the following error while "
                f"writing file {self.filename}:\n\n {ffmpeg_error}"
            )

            if "Unknown encoder" in ffmpeg_error:
                error += (
                    "\n\nThe video export failed because FFMPEG didn't find the "
                    f"specified codec for video encoding {self.codec}. "
                    "Please install this codec or change the codec when calling "
                    "write_videofile.\nFor instance:\n"
                    "  >>> clip.write_videofile('myvid.webm', codec='libvpx')"
                )

            elif "incorrect codec parameters ?" in ffmpeg_error:
                error += (
                    "\n\nThe video export failed, possibly because the codec "
                    f"specified for the video {self.codec} is not compatible with "
                    f"the given extension {self.ext}.\n"
                    "Please specify a valid 'codec' argument in write_videofile.\n"
                    "This would be 'libx264' or 'mpeg4' for mp4, "
                    "'libtheora' for ogv, 'libvpx for webm.\n"
                    "Another possible reason is that the audio codec was not "
                    "compatible with the video codec. For instance, the video "
                    "extensions 'ogv' and 'webm' only allow 'libvorbis' (default) as a"
                    "video codec."
                )

            elif "bitrate not specified" in ffmpeg_error:

                error += (
                    "\n\nThe video export failed, possibly because the bitrate "
                    "specified was too high or too low for the video codec."
                )

            elif "Invalid encoder type" in ffmpeg_error:

                error += (
                    "\n\nThe video export failed because the codec "
                    "or file extension you provided is not suitable for video"
                )

            raise IOError(error)

    def close(self):
        if self.proc:
            self.proc.stdin.close()
            if self.proc.stderr is not None:
                self.proc.stderr.close()
            self.proc.wait()

            self.proc = None

    # Support the Context Manager protocol, to ensure that resources are cleaned up.

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


def ffmpeg_write_video(
    clip,
    filename,
    fps,
    codec="libx264",
    bitrate=None,
    preset="medium",
    withmask=False,
    write_logfile=False,
    audiofile=None,
    threads=None,
    ffmpeg_params=None,
    logger="bar",
    pix_fmt=None,
):
    """Write the clip to a videofile. See VideoClip.write_videofile for details
    on the parameters.
    """
    logger = proglog.default_bar_logger(logger)

    if write_logfile:
        logfile = open(filename + ".log", "w+")
    else:
        logfile = None
    logger(message="Moviepy - Writing video %s\n" % filename)
    if not pix_fmt:
        pix_fmt = "rgba" if withmask else "rgb24"
    with FFMPEG_VideoWriter(
        filename,
        clip.size,
        fps,
        codec=codec,
        preset=preset,
        bitrate=bitrate,
        logfile=logfile,
        audiofile=audiofile,
        threads=threads,
        ffmpeg_params=ffmpeg_params,
        pix_fmt=pix_fmt,
    ) as writer:
        for t, frame in clip.iter_frames(
            logger=logger, with_times=True, fps=fps, dtype="uint8"
        ):
            if withmask:
                mask = 255 * clip.mask.get_frame(t)
                if mask.dtype != "uint8":
                    mask = mask.astype("uint8")
                frame = np.dstack([frame, mask])

            writer.write_frame(frame)

    if write_logfile:
        logfile.close()
    logger(message="Moviepy - Done !")


def ffmpeg_write_image(filename, image, logfile=False, pix_fmt=None):
    """Writes an image (HxWx3 or HxWx4 numpy array) to a file, using
    ffmpeg."""

    if image.dtype != "uint8":
        image = image.astype("uint8")
    if not pix_fmt:
        pix_fmt = "rgba" if (image.shape[2] == 4) else "rgb24"

    cmd = [
        FFMPEG_BINARY,
        "-y",
        "-s",
        "%dx%d" % (image.shape[:2][::-1]),
        "-f",
        "rawvideo",
        "-pix_fmt",
        pix_fmt,
        "-i",
        "-",
        filename,
    ]

    if logfile:
        log_file = open(filename + ".log", "w+")
    else:
        log_file = sp.PIPE

    popen_params = {"stdout": sp.DEVNULL, "stderr": log_file, "stdin": sp.PIPE}

    if os.name == "nt":
        popen_params["creationflags"] = 0x08000000

    proc = sp.Popen(cmd, **popen_params)
    out, err = proc.communicate(image.tostring())

    if proc.returncode:
        error = (
            f"{err}\n\nMoviePy error: FFMPEG encountered the following error while "
            f"writing file {filename} with command {cmd}:\n\n {err.decode()}"
        )

        raise IOError(error)

    del proc
