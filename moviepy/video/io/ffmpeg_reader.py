"""
This module implements all the functions to read a video or a picture
using ffmpeg. It is quite ugly, as there are many pitfalls to avoid
"""

from __future__ import division

import logging
import os
import re
import subprocess as sp
import warnings

import numpy as np

from moviepy.config import FFMPEG_BINARY  # ffmpeg, ffmpeg.exe, etc...
from moviepy.tools import cvsecs

logging.captureWarnings(True)


class FFMPEG_VideoReader:
    def __init__(
        self,
        filename,
        print_infos=False,
        bufsize=None,
        pixel_format="rgb24",
        check_duration=True,
        target_resolution=None,
        resize_algo="bicubic",
        fps_source="tbr",
    ):

        self.filename = filename
        self.proc = None
        infos = ffmpeg_parse_infos(filename, print_infos, check_duration, fps_source)
        self.fps = infos["video_fps"]
        self.size = infos["video_size"]
        self.rotation = infos["video_rotation"]

        if target_resolution:
            if None in target_resolution:
                ratio = 1
                for idx, target in enumerate(target_resolution):
                    if target:
                        ratio = target / self.size[idx]
                self.size = (int(self.size[0] * ratio), int(self.size[1] * ratio))
            else:
                self.size = target_resolution
        self.resize_algo = resize_algo

        self.duration = infos["video_duration"]
        self.ffmpeg_duration = infos["duration"]
        self.nframes = infos["video_nframes"]

        self.infos = infos

        self.pixel_format = pixel_format
        self.depth = 4 if pixel_format == "rgba" else 3

        if bufsize is None:
            w, h = self.size
            bufsize = self.depth * w * h + 100

        self.bufsize = bufsize
        self.initialize()

        self.pos = 1
        self.last_read = self.read_frame()

    def initialize(self, start_time=0):
        """Opens the file, creates the pipe. """

        self.close()  # if any

        if start_time != 0:
            offset = min(1, start_time)
            i_arg = [
                "-ss",
                "%.06f" % (start_time - offset),
                "-i",
                self.filename,
                "-ss",
                "%.06f" % offset,
            ]
        else:
            i_arg = ["-i", self.filename]

        cmd = (
            [FFMPEG_BINARY]
            + i_arg
            + [
                "-loglevel",
                "error",
                "-f",
                "image2pipe",
                "-vf",
                "scale=%d:%d" % tuple(self.size),
                "-sws_flags",
                self.resize_algo,
                "-pix_fmt",
                self.pixel_format,
                "-vcodec",
                "rawvideo",
                "-",
            ]
        )
        popen_params = {
            "bufsize": self.bufsize,
            "stdout": sp.PIPE,
            "stderr": sp.PIPE,
            "stdin": sp.DEVNULL,
        }

        if os.name == "nt":
            popen_params["creationflags"] = 0x08000000

        self.proc = sp.Popen(cmd, **popen_params)

    def skip_frames(self, n=1):
        """Reads and throws away n frames """
        w, h = self.size
        for i in range(n):
            self.proc.stdout.read(self.depth * w * h)
            # self.proc.stdout.flush()
        self.pos += n

    def read_frame(self):
        w, h = self.size
        nbytes = self.depth * w * h

        s = self.proc.stdout.read(nbytes)
        if len(s) != nbytes:

            warnings.warn(
                "Warning: in file %s, " % (self.filename)
                + "%d bytes wanted but %d bytes read," % (nbytes, len(s))
                + "at frame %d/%d, at time %.02f/%.02f sec. "
                % (self.pos, self.nframes, 1.0 * self.pos / self.fps, self.duration)
                + "Using the last valid frame instead.",
                UserWarning,
            )

            if not hasattr(self, "last_read"):
                raise IOError(
                    (
                        "MoviePy error: failed to read the first frame of "
                        "video file %s. That might mean that the file is "
                        "corrupted. That may also mean that you are using "
                        "a deprecated version of FFMPEG. On Ubuntu/Debian "
                        "for instance the version in the repos is deprecated. "
                        "Please update to a recent version from the website."
                    )
                    % (self.filename)
                )

            result = self.last_read

        else:
            if hasattr(np, "frombuffer"):
                result = np.frombuffer(s, dtype="uint8")
            else:
                result = np.fromstring(s, dtype="uint8")
            result.shape = (h, w, len(s) // (w * h))  # reshape((h, w, len(s)//(w*h)))
            self.last_read = result

        return result

    def get_frame(self, t):
        """ Read a file video frame at time t.

        Note for coders: getting an arbitrary frame in the video with
        ffmpeg can be painfully slow if some decoding has to be done.
        This function tries to avoid fetching arbitrary frames
        whenever possible, by moving between adjacent frames.
        """

        # these definitely need to be rechecked sometime. Seems to work.

        # I use that horrible '+0.00001' hack because sometimes due to numerical
        # imprecisions a 3.0 can become a 2.99999999... which makes the int()
        # go to the previous integer. This makes the fetching more robust in the
        # case where you get the nth frame by writing get_frame(n/fps).

        pos = int(self.fps * t + 0.00001) + 1

        # Initialize proc if it is not open
        if not self.proc:
            self.initialize(t)
            self.pos = pos
            self.last_read = self.read_frame()

        if pos == self.pos:
            return self.last_read
        elif (pos < self.pos) or (pos > self.pos + 100):
            self.initialize(t)
            self.pos = pos
        else:
            self.skip_frames(pos - self.pos - 1)
        result = self.read_frame()
        self.pos = pos
        return result

    def close(self):
        if self.proc:
            self.proc.terminate()
            self.proc.stdout.close()
            self.proc.stderr.close()
            self.proc.wait()
            self.proc = None
        if hasattr(self, "last_read"):
            del self.last_read

    def __del__(self):
        self.close()


def ffmpeg_read_image(filename, with_mask=True):
    """ Read an image file (PNG, BMP, JPEG...).

    Wraps FFMPEG_Videoreader to read just one image.
    Returns an ImageClip.

    This function is not meant to be used directly in MoviePy,
    use ImageClip instead to make clips out of image files.

    Parameters
    -----------

    filename
      Name of the image file. Can be of any format supported by ffmpeg.

    with_mask
      If the image has a transparency layer, ``with_mask=true`` will save
      this layer as the mask of the returned ImageClip

    """
    pixel_format = "rgba" if with_mask else "rgb24"
    reader = FFMPEG_VideoReader(
        filename, pixel_format=pixel_format, check_duration=False
    )
    im = reader.last_read
    del reader
    return im


def ffmpeg_parse_infos(
    filename, print_infos=False, check_duration=True, fps_source="tbr"
):
    """Get file infos using ffmpeg.

    Returns a dictionnary with the fields:
    "video_found", "video_fps", "duration", "video_nframes",
    "video_duration", "audio_found", "audio_fps"

    "video_duration" is slightly smaller than "duration" to avoid
    fetching the uncomplete frames at the end, which raises an error.

    """

    # open the file in a pipe, provoke an error, read output
    is_gif = filename.endswith(".gif")
    cmd = [FFMPEG_BINARY, "-i", filename]
    if is_gif:
        cmd += ["-f", "null", "/dev/null"]

    popen_params = {
        "bufsize": 10 ** 5,
        "stdout": sp.PIPE,
        "stderr": sp.PIPE,
        "stdin": sp.DEVNULL,
    }

    if os.name == "nt":
        popen_params["creationflags"] = 0x08000000

    proc = sp.Popen(cmd, **popen_params)
    (output, error) = proc.communicate()
    infos = error.decode("utf8")

    del proc

    if print_infos:
        # print the whole info text returned by FFMPEG
        print(infos)

    lines = infos.splitlines()
    if "No such file or directory" in lines[-1]:
        raise IOError(
            (
                "MoviePy error: the file %s could not be found!\n"
                "Please check that you entered the correct "
                "path."
            )
            % filename
        )

    result = dict()

    # get duration (in seconds)
    result["duration"] = None

    if check_duration:
        try:
            keyword = "frame=" if is_gif else "Duration: "
            # for large GIFS the "full" duration is presented as the last element in the list.
            index = -1 if is_gif else 0
            line = [line for line in lines if keyword in line][index]
            match = re.findall("([0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9])", line)[0]
            result["duration"] = cvsecs(match)
        except Exception:
            raise IOError(
                (
                    "MoviePy error: failed to read the duration of file %s.\n"
                    "Here are the file infos returned by ffmpeg:\n\n%s"
                )
                % (filename, infos)
            )

    # get the output line that speaks about video
    lines_video = [
        line for line in lines if " Video: " in line and re.search(r"\d+x\d+", line)
    ]

    result["video_found"] = lines_video != []

    if result["video_found"]:
        try:
            line = lines_video[0]

            # get the size, of the form 460x320 (w x h)
            match = re.search(" [0-9]*x[0-9]*(,| )", line)
            size = list(map(int, line[match.start() : match.end() - 1].split("x")))
            result["video_size"] = size
        except Exception:
            raise IOError(
                (
                    "MoviePy error: failed to read video dimensions in file %s.\n"
                    "Here are the file infos returned by ffmpeg:\n\n%s"
                )
                % (filename, infos)
            )

        # Get the frame rate. Sometimes it's 'tbr', sometimes 'fps', sometimes
        # tbc, and sometimes tbc/2...
        # Current policy: Trust tbr first, then fps unless fps_source is
        # specified as 'fps' in which case try fps then tbr

        # If result is near from x*1000/1001 where x is 23,24,25,50,
        # replace by x*1000/1001 (very common case for the fps).

        def get_tbr():
            match = re.search("( [0-9]*.| )[0-9]* tbr", line)

            # Sometimes comes as e.g. 12k. We need to replace that with 12000.
            s_tbr = line[match.start() : match.end()].split(" ")[1]
            if "k" in s_tbr:
                tbr = float(s_tbr.replace("k", "")) * 1000
            else:
                tbr = float(s_tbr)
            return tbr

        def get_fps():
            match = re.search("( [0-9]*.| )[0-9]* fps", line)
            fps = float(line[match.start() : match.end()].split(" ")[1])
            return fps

        if fps_source == "tbr":
            try:
                result["video_fps"] = get_tbr()
            except Exception:
                result["video_fps"] = get_fps()

        elif fps_source == "fps":
            try:
                result["video_fps"] = get_fps()
            except Exception:
                result["video_fps"] = get_tbr()

        # It is known that a fps of 24 is often written as 24000/1001
        # but then ffmpeg nicely rounds it to 23.98, which we hate.
        coef = 1000.0 / 1001.0
        fps = result["video_fps"]
        for x in [23, 24, 25, 30, 50]:
            if (fps != x) and abs(fps - x * coef) < 0.01:
                result["video_fps"] = x * coef

        if check_duration:
            result["video_nframes"] = int(result["duration"] * result["video_fps"]) + 1
            result["video_duration"] = result["duration"]
        else:
            result["video_nframes"] = 1
            result["video_duration"] = None
        # We could have also recomputed the duration from the number
        # of frames, as follows:
        # >>> result['video_duration'] = result['video_nframes'] / result['video_fps']

        # get the video rotation info.
        try:
            rotation_lines = [
                line
                for line in lines
                if "rotate          :" in line and re.search(r"\d+$", line)
            ]
            if len(rotation_lines):
                rotation_line = rotation_lines[0]
                match = re.search(r"\d+$", rotation_line)
                result["video_rotation"] = int(
                    rotation_line[match.start() : match.end()]
                )
            else:
                result["video_rotation"] = 0
        except Exception:
            raise IOError(
                (
                    "MoviePy error: failed to read video rotation in file %s.\n"
                    "Here are the file infos returned by ffmpeg:\n\n%s"
                )
                % (filename, infos)
            )

    lines_audio = [l for l in lines if " Audio: " in l]

    result["audio_found"] = lines_audio != []

    if result["audio_found"]:
        line = lines_audio[0]
        try:
            match = re.search(" [0-9]* Hz", line)
            hz_string = line[
                match.start() + 1 : match.end() - 3
            ]  # Removes the 'hz' from the end
            result["audio_fps"] = int(hz_string)
        except Exception:
            result["audio_fps"] = "unknown"

    return result
