"""Implements all the functions to read a video or a picture using ffmpeg."""

import os
import re
import subprocess as sp
import warnings
from typing import List

import numpy as np

from moviepy.config import FFMPEG_BINARY  # ffmpeg, ffmpeg.exe, etc...
from moviepy.tools import (
    convert_to_seconds,
    cross_platform_popen_params,
    ffmpeg_escape_filename,
)
from moviepy.video.io.errors import VideoCorruptedError


class FFMPEG_VideoReader:
    """Class for video byte-level reading with ffmpeg."""

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
            filename,
            check_duration=check_duration,
            fps_source=fps_source,
            decode_file=decode_file,
            print_infos=print_infos,
        )
        # If framerate is unavailable, assume 1.0 FPS to avoid divide-by-zero errors.
        self.fps = infos.get("video_fps", 1.0)
        # If frame size is unavailable, set 1x1 divide-by-zero errors.
        self.size = infos.get("video_size", (1, 1))

        # ffmpeg automatically rotates videos if rotation information is
        # available, so exchange width and height
        self.rotation = abs(infos.get("video_rotation", 0))
        if self.rotation in [90, 270]:
            self.size = [self.size[1], self.size[0]]

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

        self.duration = infos.get("video_duration", 0.0)
        self.ffmpeg_duration = infos.get("duration", 0.0)
        self.n_frames = infos.get("video_n_frames", 0)
        self.bitrate = infos.get("video_bitrate", 0)

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
        it pre-reads the first frame).
        """
        self.close(delete_lastread=False)  # if any

        # self.pos represents the (0-indexed) index of the frame that is next in line
        # to be read by self.read_frame().
        # Eg when self.pos is 1, the 2nd frame will be read next.
        self.pos = self.get_frame_number(start_time)

        # Getting around a difference between ffmpeg and moviepy seeking:
        # "moviepy seek" means "get the frame displayed at time t"
        #   Hence given a 29.97 FPS video, seeking to .01s means "get frame 0".
        # "ffmpeg seek" means "skip all frames until you reach time t".
        #   This time, seeking to .01s means "get frame 1". Surprise!
        #
        # (In 30fps, timestamps like 2.0s, 3.5s will give the same frame output
        # under both rules, for the timestamp can be represented exactly in
        # decimal.)
        #
        # So we'll subtract an epsilon from the timestamp given to ffmpeg.
        if self.pos != 0:
            start_time = self.pos * (1 / self.fps) - 0.00001
        else:
            start_time = 0.0

        if start_time != 0:
            offset = min(1, start_time)
            i_arg = [
                "-ss",
                "%.06f" % (start_time - offset),
                "-i",
                ffmpeg_escape_filename(self.filename),
                "-ss",
                "%.06f" % offset,
            ]
        else:
            i_arg = ["-i", ffmpeg_escape_filename(self.filename)]

        # For webm video (vp8 and vp9) with transparent layer, force libvpx/libvpx-vp9
        # as ffmpeg native webm decoder dont decode alpha layer
        # (see
        # https://www.reddit.com/r/ffmpeg/comments/fgpyfb/help_with_webm_with_alpha_channel/
        # )
        if self.depth == 4:
            codec_name = self.infos.get("video_codec_name")
            if codec_name == "vp9":
                i_arg = ["-c:v", "libvpx-vp9"] + i_arg
            elif codec_name == "vp8":
                i_arg = ["-c:v", "libvpx"] + i_arg

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
        self.last_read = self.read_frame()

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
        and stored in ``self.last_read``.
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
        # after the frame is read. This makes the later comparisons easier.
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
            return self.last_read
        else:
            # If pos == self.pos + 1, this line has no effect
            self.skip_frames(pos - self.pos - 1)
            result = self.read_frame()
            return result

    @property
    def lastread(self):
        """Alias of `self.last_read` for backwards compatibility with MoviePy 1.x."""
        return self.last_read

    def get_frame_number(self, t):
        """Helper method to return the frame number at time ``t``"""
        # I used this horrible '+0.00001' hack because sometimes due to numerical
        # imprecisions a 3.0 can become a 2.99999999... which makes the int()
        # go to the previous integer. This makes the fetching more robust when you
        # are getting the nth frame by writing get_frame(n/fps).
        return int(self.fps * t + 0.00001)

    def close(self, delete_lastread=True):
        """Closes the reader terminating the process, if is still open."""
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
    ----------

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


class FFmpegInfosParser:
    """An (hopefully) robuste ffmpeg `-i` command option file information parser.
    Is designed to parse the output by extracting the different blocks of informations,
    based on the indentation, in order to create an easy to handle block tree

    Parameters
    ----------

    filename
      Name of the file parsed, only used to raise accurate error messages.

    infos
      Information returned by FFmpeg.

    fps_source
      Indicates what source data will be preferably used to retrieve fps data.

    check_duration
      Enable or disable the parsing of the duration of the file. Useful to
      skip the duration check, for example, for images.

    decode_file
      Indicates if the whole file has been decoded. The duration parsing strategy
      will differ depending on this argument.
    """

    class ParseDimensionError(VideoCorruptedError):
        """Error raised when we cannot find dimensions in a video stream"""

        pass

    class ParseDurationError(VideoCorruptedError):
        """Error raised when we cannot find duration in a video stream"""

        pass

    class InfoBlock:
        """Represents a block of output from ffmpeg, which can be an input file,
        stream, chapter or metadata.
        """

        def __init__(self, block_line, indent_level=0):
            self.type = "unknown"
            self.childs: List[FFmpegInfosParser.InfoBlock] = []
            self.parent = None
            self.indent_level = indent_level
            self.head_line = block_line
            self.raw_data = []
            self.data = {}

        def add_child(self, child):
            """Adds a child to the current block."""
            child.parent = self
            self.childs.append(child)

    def __init__(
        self,
        infos,
        filename,
        fps_source="fps",
        check_duration=True,
        decode_file=False,
    ):
        self.infos = infos
        self.filename = filename
        self.check_duration = check_duration
        self.fps_source = fps_source
        self.duration_tag_separator = "time=" if decode_file else "Duration: "
        self.blocks = None
        self.video_stream = None
        self.audio_stream = None
        self.data_stream = None

        self.result = {
            "video_found": False,
            "audio_found": False,
            "metadata": {},
            "blocks": None,
            "inputs": {},
        }

    def _extract_block(self, index, start_indent, block: InfoBlock = None):
        lines = self.infos.splitlines()
        block.content = []
        multiline = None
        is_last_line = False
        while index < len(lines) - 1:
            index += 1
            is_last_line = index == (len(lines) - 1)
            line = lines[index]
            indent_level = (len(line) - len(line.lstrip())) / 2
            line = line.strip()

            if not is_last_line:
                next_line = lines[index + 1].strip()
            else:
                next_line = False

            # End of block
            if indent_level <= start_indent:
                index -= 1
                break

            # New block
            if line.lstrip().startswith(
                ("Metadata", "Stream", "Side data", "Chapter", "Chapters")
            ):
                (child_block, index) = self._extract_block(
                    index, indent_level, self.InfoBlock(line.lstrip(), indent_level)
                )
                self._parse_headline_data(child_block)
                block.add_child(child_block)
                continue

            # Support for multiline entries
            if line.startswith(":") or (next_line and next_line.startswith(":")):
                if not multiline:
                    multiline = line
                    continue
                elif next_line.startswith(":"):
                    multiline += "\n" + line[1:].strip()
                    continue

            if multiline:
                line = multiline + "\n" + line[1:].strip()
                multiline = None

            # Standard line, add to block raw data and parsed data
            block.raw_data.append(line)
            field, value = self._parse_line(line)
            block.data[field] = value

        return (block, index)

    def _parse_headline_data(self, block: InfoBlock):
        line = block.head_line.lstrip()
        if line.startswith("Input "):
            block.type = "input"
        elif line.startswith("Metadata:"):
            block.type = "metadata"
        elif line.startswith("Stream "):
            block.type = "stream"
            self._parse_stream(block)
        elif line.startswith("Side data:"):
            block.type = "side_data"
        elif line.startswith("Chapters"):
            block.type = "chapters"
        elif line.startswith("Chapter"):
            block.type = "chapter"
            self._parse_chapter(block)

    def _parse_line(self, line):
        """Parse a standard line to return (field, value) with typecasting
        when needed (rotate, displaymatrix)
        """
        specials = (
            "Ambient Viewing Environment,",
            "Content Light Level Metadata,",
            "Mastering Display Metadata,",
        )
        line = line.strip()
        if line.startswith(specials):
            infos = line.split(",", 1)
        else:
            infos = line.split(":", 1)

        field = infos[0].strip()
        value = infos[1].strip()

        if field == "rotate":
            value = float(value)

        elif field == "displaymatrix":
            match = re.search(r"[-+]?\d+(\.\d+)?", value)
            if match:
                # We must multiply by -1 because displaymatrix return info
                # about how to rotate to show video, not about video rotation
                value = float(match.group()) * -1

        return (field, value)

    def _parse_duration(self, line):
        """Parse the duration from the block data."""
        try:
            match_duration = re.search(
                r"([0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9])",
                line,
            )
            if match_duration is None:
                raise VideoCorruptedError(f"Could not parse duration from {line!r}")
            return convert_to_seconds(match_duration.group(1))
        except VideoCorruptedError:
            raise
        except Exception:
            raise IOError(
                (
                    "MoviePy error: failed to read the duration of file '%s'.\n"
                    "Here are the file infos returned by ffmpeg:\n\n%s"
                )
                % (self.filename, self.infos)
            )

    def _parse_stream(self, block: InfoBlock):
        # get input number, stream number, language and type
        main_info_match = re.search(
            r"^Stream\s#(\d+):(\d+)(?:\[\w+\])?\(?(\w+)?\)?:\s(\w+):",
            block.head_line.lstrip(),
        )
        (
            input_number,
            stream_number,
            language,
            stream_type,
        ) = main_info_match.groups()
        block.data["input_number"] = int(input_number)
        block.data["stream_number"] = int(stream_number)
        block.data["stream_type_lower"] = stream_type.lower()

        if language == "und":
            language = None

        block.data["language"] = language
        block.data["default"] = block.head_line.rstrip().endswith("(default)")

        if block.data["stream_type_lower"] == "audio":
            self._parse_stream_audio(block)
        elif block.data["stream_type_lower"] == "video":
            self._parse_stream_video(block)
        elif block.data["stream_type_lower"] == "data":
            self._parse_stream_data(block)

    def _parse_stream_audio(self, block: InfoBlock):
        """Parses data from "Stream ... Audio" line."""
        try:
            block.data["fps"] = int(re.search(r" (\d+) Hz", block.head_line).group(1))
        except (AttributeError, ValueError):
            # AttributeError: 'NoneType' object has no attribute 'group'
            # ValueError: invalid literal for int() with base 10: '<string>'
            block.data["fps"] = "unknown"

        match_audio_bitrate = re.search(r"(\d+) k(i?)b/s", block.head_line)
        block.data["bitrate"] = (
            int(match_audio_bitrate.group(1)) if match_audio_bitrate else None
        )

        # Store default stream, or first stream if we dont find any default
        if block.data["default"] or not self.audio_stream:
            self.audio_stream = block

    def _parse_stream_data(self, block: InfoBlock):
        """Parses data from "Stream ... Data" line."""
        # Store default stream, or first stream if we dont find any default
        if block.data["default"] or not self.data_stream:
            self.data_stream = block

    def _parse_stream_video(self, block: InfoBlock):
        """Parses data from "Stream ... Video" line."""
        try:
            match_video_size = re.search(r" (\d+)x(\d+)[,\s]", block.head_line)
            if match_video_size:
                # size, of the form 460x320 (w x h)
                block.data["size"] = [int(num) for num in match_video_size.groups()]
        except Exception:
            raise FFmpegInfosParser.ParseDimensionError()

        match_bitrate = re.search(r"(\d+) k(i?)b/s", block.head_line)
        block.data["bitrate"] = int(match_bitrate.group(1)) if match_bitrate else None

        # Get the frame rate. Sometimes it's 'tbr', sometimes 'fps', sometimes
        # tbc, and sometimes tbc/2...
        # Current policy: Trust fps first, then tbr unless fps_source is
        # specified as 'tbr' in which case try tbr then fps

        # If result is near from x*1000/1001 where x is 23,24,25,50,
        # replace by x*1000/1001 (very common case for the fps).

        if self.fps_source == "fps":
            try:
                fps = self._parse_fps(block.head_line)
            except (AttributeError, ValueError):
                fps = self._parse_tbr(block.head_line)
        elif self.fps_source == "tbr":
            try:
                fps = self._parse_tbr(block.head_line)
            except (AttributeError, ValueError):
                fps = self._parse_fps(block.head_line)
        else:
            raise ValueError(
                ("fps source '%s' not supported parsing the video '%s'")
                % (self.fps_source, self.filename)
            )

        # It is known that a fps of 24 is often written as 24000/1001
        # but then ffmpeg nicely rounds it to 23.98, which we hate.
        coef = 1000.0 / 1001.0
        for x in [23, 24, 25, 30, 50]:
            if (fps != x) and abs(fps - x * coef) < 0.01:
                fps = x * coef
        block.data["fps"] = fps

        # Try to extract video codec and profile
        main_info_match = re.search(
            r"Video:\s(\w+)?\s?(\([^)]+\))?",
            block.head_line.lstrip(),
        )

        if main_info_match is not None:
            (codec_name, profile) = main_info_match.groups()
            block.data["codec_name"] = codec_name
            block.data["profile"] = profile

        # Store default stream, or first stream if we dont find any default
        if block.data["default"] or not self.video_stream:
            self.video_stream = block

    def _parse_fps(self, line):
        """Parses number of FPS from a line of the ``ffmpeg -i`` command output."""
        return float(re.search(r" (\d+.?\d*) fps", line).group(1))

    def _parse_tbr(self, line):
        """Parses number of TBS from a line of the ``ffmpeg -i`` command output."""
        s_tbr = re.search(r" (\d+.?\d*k?) tbr", line).group(1)

        # Sometimes comes as e.g. 12k. We need to replace that with 12000.
        if s_tbr[-1] == "k":
            tbr = float(s_tbr[:-1]) * 1000
        else:
            tbr = float(s_tbr)
        return tbr

    def _parse_chapter(self, block: InfoBlock):
        # extract chapter data
        chapter_data_match = re.search(
            r"^Chapter #(\d+):(\d+): start (\d+\.?\d+?), end (\d+\.?\d+?)",
            block.head_line.strip(),
        )
        input_number, chapter_number, start, end = chapter_data_match.groups()

        # start building the chapter
        block.data = {
            "input_number": int(input_number),
            "chapter_number": int(chapter_number),
            "start": float(start),
            "end": float(end),
        }

    def _parse_blocks(self, root: InfoBlock):
        for key, data in root.data.items():
            if key == "Duration":
                self.result["duration"] = self._parse_duration(data)

                bitrate_match = re.search(r"bitrate: (\d+) k(i?)b/s", data)
                self.result["bitrate"] = (
                    int(bitrate_match.group(1)) if bitrate_match else None
                )

                start_match = re.search(r"start: (\d+\.?\d+)", data)
                self.result["start"] = (
                    float(start_match.group(1)) if start_match else None
                )
            else:
                if "metadata" not in self.result:
                    self.result["metadata"] = {}

                self.result["metadata"][key] = data

        # For input direct metadata blocks, add meta to results
        for child in root.childs:
            if child.type in ("metadata", "side_data"):
                for key, data in child.data.items():
                    if "metadata" not in self.result:
                        self.result["metadata"] = {}

                    self.result["metadata"][key] = data

        if self.video_stream:
            self.result["video_found"] = True
            self.result["video_size"] = self.video_stream.data.get("size", None)
            self.result["video_bitrate"] = self.video_stream.data.get("bitrate", None)
            self.result["video_fps"] = self.video_stream.data["fps"]
            self.result["video_codec_name"] = self.video_stream.data.get(
                "codec_name", None
            )
            self.result["video_profile"] = self.video_stream.data.get("profile", None)
            for child in self.video_stream.childs:
                if child.type in ("metadata", "side_data"):
                    for key, data in child.data.items():
                        if key in ("rotate", "displaymatrix"):
                            self.result["video_rotation"] = data

        if self.audio_stream:
            self.result["audio_found"] = True
            self.result["audio_fps"] = self.audio_stream.data["fps"]
            self.result["audio_bitrate"] = self.audio_stream.data["bitrate"]

        if self.result["video_found"] and self.check_duration:
            if "duration" not in self.result:
                raise self.ParseDurationError()

            self.result["video_duration"] = self.result["duration"]
            self.result["video_n_frames"] = int(
                self.result["duration"] * self.result.get("video_fps", 0)
            )
        else:
            self.result["video_n_frames"] = 0
            self.result["video_duration"] = 0.0

        self._populate_inputs(root=root)

    def _populate_inputs(self, root: InfoBlock):
        """Forge inputs for compatibility with old versions, not used anywhere though"""
        for child in root.childs:
            if child.type == "stream":
                if "streams" not in self.result["inputs"]:
                    self.result["inputs"]["streams"] = []

                stream = child.data

                for stream_child in child.childs:
                    if stream_child.type == "metadata":
                        stream["metadata"] = stream_child.data
                    elif stream_child.type == "side_data":
                        stream["side_data"] = stream_child.data

                self.result["inputs"]["streams"].append(stream)

            elif child.type == "chapters":
                for chapter in child.childs:
                    if "chapters" not in self.result["inputs"]:
                        self.result["inputs"]["chapters"] = []

                    chap = chapter.data

                    for chapter_child in chapter.childs:
                        if chapter_child.type == "metadata":
                            chap["metadata"] = chapter_child.data
                        elif chapter_child.type == "side_data":
                            chap["side_data"] = chapter_child.data

                    self.result["inputs"]["chapters"].append(chap)

            elif child.type == "metadata":
                self.result["metadata"] = child.data

        if self.audio_stream:
            self.result["default_audio_input_number"] = self.audio_stream.data[
                "input_number"
            ]
            self.result["default_audio_stream_number"] = self.audio_stream.data[
                "stream_number"
            ]

        if self.video_stream:
            self.result["default_video_input_number"] = self.video_stream.data[
                "input_number"
            ]
            self.result["default_video_stream_number"] = self.video_stream.data[
                "stream_number"
            ]

        if self.data_stream:
            self.result["default_data_input_number"] = self.data_stream.data[
                "input_number"
            ]
            self.result["default_data_stream_number"] = self.data_stream.data[
                "stream_number"
            ]

    def parse(self):
        """Parses the information returned by FFmpeg in stderr executing their binary
        for a file with ``-i`` option and returns a dictionary with all data needed
        by MoviePy.
        """
        try:
            first_input = 0
            for line in self.infos.splitlines():
                if line.startswith("Input"):
                    break
                first_input += 1

            root_block = self.InfoBlock(self.infos.splitlines()[first_input], 0)
            self._extract_block(first_input, 0, root_block)
            self._parse_blocks(root_block)
            self.blocks = root_block
            self.result["blocks"] = root_block
            return self.result
        except self.ParseDimensionError:
            raise IOError(
                (
                    "MoviePy error: failed to read video dimensions in"
                    " file '%s'.\nHere are the file infos returned by"
                    "ffmpeg:\n\n%s"
                )
                % (self.filename, self.infos)
            )
        except self.ParseDurationError:
            raise IOError(
                (
                    "MoviePy error: failed to read video duration in"
                    " file '%s'.\nHere are the file infos returned by"
                    "ffmpeg:\n\n%s"
                )
                % (self.filename, self.infos)
            )


def ffmpeg_parse_infos(
    filename,
    check_duration=True,
    fps_source="fps",
    decode_file=False,
    print_infos=False,
):
    """Get the information of a file using ffmpeg.

    Returns a dictionary with next fields:

    - ``"audio_bitrate"``
    - ``"audio_found"``
    - ``"audio_fps"``
    - ``"bitrate"``
    - ``"duration"``
    - ``"inputs"``
    - ``"metadata"``
    - ``"start"``
    - ``"video_bitrate"``
    - ``"video_codec_name"``
    - ``"video_duration"``
    - ``"video_fps"``
    - ``"video_found"``
    - ``"video_n_frames"``
    - ``"video_profile"``
    - ``"video_rotation"``
    - ``"video_size"``

    Note that "video_duration" is slightly smaller than "duration" to avoid
    fetching the incomplete frames at the end, which raises an error.

    Parameters
    ----------

    filename
      Name of the file parsed, only used to raise accurate error messages.

    infos
      Information returned by FFmpeg.

    fps_source
      Indicates what source data will be preferably used to retrieve fps data.

    check_duration
      Enable or disable the parsing of the duration of the file. Useful to
      skip the duration check, for example, for images.

    decode_file
      Indicates if the whole file must be read to retrieve their duration.
      This is needed for some files in order to get the correct duration (see
      https://github.com/Zulko/moviepy/pull/1222).
    """
    # Open the file in a pipe, read output
    cmd = [FFMPEG_BINARY, "-hide_banner", "-i", ffmpeg_escape_filename(filename)]
    if decode_file:
        cmd.extend(["-f", "null", "-"])

    popen_params = cross_platform_popen_params(
        {
            "bufsize": 10**5,
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

    try:
        return FFmpegInfosParser(
            infos,
            filename,
            fps_source=fps_source,
            check_duration=check_duration,
            decode_file=decode_file,
        ).parse()
    except VideoCorruptedError:
        raise
    except Exception as exc:
        if os.path.isdir(filename):
            raise IsADirectoryError(f"'{filename}' is a directory")
        elif not os.path.exists(filename):
            raise FileNotFoundError(f"'{filename}' not found")
        raise IOError(f"Error passing `ffmpeg -i` command output: \n\n{infos}") from exc
