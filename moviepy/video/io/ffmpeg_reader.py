"""
This module implements all the functions to read a video or a picture
using ffmpeg. It is quite ugly, as there are many pitfalls to avoid
"""

import re
import subprocess as sp
import warnings

import numpy as np

from moviepy.config import FFMPEG_BINARY  # ffmpeg, ffmpeg.exe, etc...
from moviepy.tools import convert_to_seconds, cross_platform_popen_params


class FFMPEG_VideoReader:
    def __init__(
        self,
        filename,
        decode_file=True,
        print_infos=False,
        bufsize=None,
        pixel_format="rgb24",
        check_duration=True,
        target_resolution=None,
        resize_algo="bicubic",
        fps_source="fps",
    ):

        self.filename = filename
        self.proc = None
        infos = ffmpeg_parse_infos(
            filename, decode_file, print_infos, check_duration, fps_source
        )
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
        self.n_frames = infos["video_n_frames"]
        self.bitrate = infos["video_bitrate"]

        self.infos = infos

        self.pixel_format = pixel_format
        self.depth = 4 if pixel_format[-1] == "a" else 3
        # 'a' represents 'alpha' which means that each pixel has 4 values instead of 3.
        # See https://github.com/Zulko/moviepy/issues/1070#issuecomment-644457274

        if bufsize is None:
            w, h = self.size
            bufsize = self.depth * w * h + 100

        self.bufsize = bufsize
        self.initialize()

    def initialize(self, start_time=0):
        """
        Opens the file, creates the pipe.
        Sets self.pos to the appropriate value (1 if start_time == 0 because
        it pre-reads the first frame)
        """

        self.close(delete_lastread=False)  # if any

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
        popen_params = cross_platform_popen_params(
            {
                "bufsize": self.bufsize,
                "stdout": sp.PIPE,
                "stderr": sp.PIPE,
                "stdin": sp.DEVNULL,
            }
        )
        self.proc = sp.Popen(cmd, **popen_params)

        # self.pos represents the (0-indexed) index of the frame that is next in line
        # to be read by self.read_frame().
        # Eg when self.pos is 1, the 2nd frame will be read next.
        self.pos = self.get_frame_number(start_time)
        self.lastread = self.read_frame()

    def skip_frames(self, n=1):
        """Reads and throws away n frames"""
        w, h = self.size
        for i in range(n):
            self.proc.stdout.read(self.depth * w * h)

            # self.proc.stdout.flush()
        self.pos += n

    def read_frame(self):
        """
        Reads the next frame from the file.
        Note that upon (re)initialization, the first frame will already have been read
        and stored in ``self.lastread``.
        """
        w, h = self.size
        nbytes = self.depth * w * h

        s = self.proc.stdout.read(nbytes)

        if len(s) != nbytes:
            warnings.warn(
                (
                    "In file %s, %d bytes wanted but %d bytes read at frame index"
                    " %d (out of a total %d frames), at time %.02f/%.02f sec."
                    " Using the last valid frame instead."
                )
                % (
                    self.filename,
                    nbytes,
                    len(s),
                    self.pos,
                    self.n_frames,
                    1.0 * self.pos / self.fps,
                    self.duration,
                ),
                UserWarning,
            )
            if not hasattr(self, "last_read"):
                raise IOError(
                    (
                        "MoviePy error: failed to read the first frame of "
                        f"video file {self.filename}. That might mean that the file is "
                        "corrupted. That may also mean that you are using "
                        "a deprecated version of FFMPEG. On Ubuntu/Debian "
                        "for instance the version in the repos is deprecated. "
                        "Please update to a recent version from the website."
                    )
                )

            result = self.last_read

        else:
            if hasattr(np, "frombuffer"):
                result = np.frombuffer(s, dtype="uint8")
            else:
                result = np.fromstring(s, dtype="uint8")
            result.shape = (h, w, len(s) // (w * h))  # reshape((h, w, len(s)//(w*h)))
            self.last_read = result

        # We have to do this down here because `self.pos` is used in the warning above
        self.pos += 1

        return result

    def get_frame(self, t):
        """Read a file video frame at time t.

        Note for coders: getting an arbitrary frame in the video with
        ffmpeg can be painfully slow if some decoding has to be done.
        This function tries to avoid fetching arbitrary frames
        whenever possible, by moving between adjacent frames.
        """

        # + 1 so that it represents the frame position that it will be
        # after the frame is read. This makes the later comparisions easier.
        pos = self.get_frame_number(t) + 1

        # Initialize proc if it is not open
        if not self.proc:
            print("Proc not detected")
            self.initialize(t)
            return self.last_read

        if pos == self.pos:
            return self.last_read
        elif (pos < self.pos) or (pos > self.pos + 100):
            # We can't just skip forward to `pos` or it would take too long
            self.initialize(t)
            return self.lastread
        else:
            # If pos == self.pos + 1, this line has no effect
            self.skip_frames(pos - self.pos - 1)
            result = self.read_frame()
            return result

    def get_frame_number(self, t):
        """Helper method to return the frame number at time ``t``"""
        # I used this horrible '+0.00001' hack because sometimes due to numerical
        # imprecisions a 3.0 can become a 2.99999999... which makes the int()
        # go to the previous integer. This makes the fetching more robust when you
        # are getting the nth frame by writing get_frame(n/fps).
        return int(self.fps * t + 0.00001)

    def close(self, delete_lastread=True):
        if self.proc:
            if self.proc.poll() is None:
                self.proc.terminate()
                self.proc.stdout.close()
                self.proc.stderr.close()
                self.proc.wait()
            self.proc = None
        if delete_lastread and hasattr(self, "last_read"):
            del self.last_read

    def __del__(self):
        self.close()


def ffmpeg_read_image(filename, with_mask=True, pixel_format=None):
    """Read an image file (PNG, BMP, JPEG...).

    Wraps FFMPEG_Videoreader to read just one image.
    Returns an ImageClip.

    This function is not meant to be used directly in MoviePy.
    Use ImageClip instead to make clips out of image files.

    Parameters
    -----------

    filename
      Name of the image file. Can be of any format supported by ffmpeg.

    with_mask
      If the image has a transparency layer, ``with_mask=true`` will save
      this layer as the mask of the returned ImageClip

    pixel_format
      Optional: Pixel format for the image to read. If is not specified
      'rgb24' will be used as the default format unless ``with_mask`` is set
      as ``True``, then 'rgba' will be used.

    """
    if not pixel_format:
        pixel_format = "rgba" if with_mask else "rgb24"
    reader = FFMPEG_VideoReader(
        filename, pixel_format=pixel_format, check_duration=False
    )
    im = reader.last_read
    del reader
    return im


def ffmpeg_parse_infos(
    filename,
    decode_file=False,
    print_infos=False,
    check_duration=True,
    fps_source="fps",
):
    """Get file infos using ffmpeg.

    Returns a dictionnary with the fields:
    "video_found", "video_fps", "duration", "video_n_frames",
    "video_duration", "video_bitrate","audio_found", "audio_fps", "audio_bitrate"

    "video_duration" is slightly smaller than "duration" to avoid
    fetching the uncomplete frames at the end, which raises an error.

    """
    # Open the file in a pipe, read output
    cmd = [FFMPEG_BINARY, "-i", filename]
    if decode_file:
        cmd.extend(["-f", "null", "-"])

    popen_params = cross_platform_popen_params(
        {
            "bufsize": 10 ** 5,
            "stdout": sp.PIPE,
            "stderr": sp.PIPE,
            "stdin": sp.DEVNULL,
        }
    )

    proc = sp.Popen(cmd, **popen_params)
    (output, error) = proc.communicate()
    infos = error.decode("utf8", errors="ignore")

    proc.terminate()
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
            if decode_file:
                line = [line for line in lines if "time=" in line][-1]
            else:
                line = [line for line in lines if "Duration:" in line][-1]
            match = re.findall("([0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9])", line)[0]
            result["duration"] = convert_to_seconds(match)
        except Exception:
            raise IOError(
                f"MoviePy error: failed to read the duration of file {filename}.\n"
                f"Here are the file infos returned by ffmpeg:\n\n{infos}"
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
        match_bit = re.search(r"(\d+) kb/s", line)
        result["video_bitrate"] = int(match_bit.group(1)) if match_bit else None

        # Get the frame rate. Sometimes it's 'tbr', sometimes 'fps', sometimes
        # tbc, and sometimes tbc/2...
        # Current policy: Trust fps first, then tbr unless fps_source is
        # specified as 'tbr' in which case try tbr then fps

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
            result["video_n_frames"] = int(result["duration"] * result["video_fps"])
            result["video_duration"] = result["duration"]
        else:
            result["video_n_frames"] = 1
            result["video_duration"] = None
        # We could have also recomputed the duration from the number
        # of frames, as follows:
        # >>> result['video_duration'] = result['video_n_frames'] / result['video_fps']

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

    lines_audio = [line for line in lines if " Audio: " in line]

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
        match_bit = re.search(r"(\d+) kb/s", line)
        result["audio_bitrate"] = int(match_bit.group(1)) if match_bit else None

    return result
