"""Implements all the functions to read a video or a picture using ffmpeg."""

import os
import re
import subprocess as sp
import warnings

import numpy as np

from moviepy.config import FFMPEG_BINARY  # ffmpeg, ffmpeg.exe, etc...
from moviepy.tools import (
    convert_to_seconds,
    cross_platform_popen_params,
    ffmpeg_escape_filename,
)


class FFMPEG_VideoReader:
    """
    通过 FFmpeg 以字节流的方式获取视频帧数据。
    它可以处理视频的解码、帧读取、视频旋转（如 90 度和 270 度）、视频大小调整等任务。
    """

    def __init__(
        self,
        filename, # 视频文件的路径。
        decode_file=True, # 是否解码整个文件来获取准确时长，默认为 True。
        print_infos=False, # 是否打印 FFmpeg 提供的元数据，默认为 False。
        bufsize=None, # 缓冲区大小，默认为 None，会根据视频大小自动计算。
        pixel_format="rgb24", # 像素格式，默认为 rgb24。
        check_duration=True, # 是否检查文件时长，默认为 True。
        target_resolution=None, # 目标视频分辨率，默认为 None，表示不调整分辨率。
        resize_algo="bicubic", # 缩放算法，默认为 bicubic（双三次插值）。
        fps_source="fps", # 获取帧率的数据来源，默认为 "fps"。
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
        打开文件，创建管道。
        设置 self.pos 为适当的值（如果 start_time == 0，则为 1，因为会预先读取第一帧）。
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
        """ 读取并丢弃 n 帧" """
        w, h = self.size
        for i in range(n):
            self.proc.stdout.read(self.depth * w * h)

            # self.proc.stdout.flush()
        self.pos += n

    def read_frame(self):
        """
        读取文件中的下一帧。
        注意：在（重新）初始化时，第一帧会已存在于 ``self.last_read`` 中。
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
        """
        读取给定时间点 t 的视频帧。

        对开发者的提醒：如果必须解码一些帧，获取任意帧的速度可能非常慢。
        该函数会尽量避免读取任意帧，而是通过移动到相邻帧来优化。
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
        """ 为了与 MoviePy 1.x 版本兼容，`self.last_read` 的别名 """
        return self.last_read

    def get_frame_number(self, t):
        """ 根据时间 t 获取视频的帧编号 """
        # I used this horrible '+0.00001' hack because sometimes due to numerical
        # imprecisions a 3.0 can become a 2.99999999... which makes the int()
        # go to the previous integer. This makes the fetching more robust when you
        # are getting the nth frame by writing get_frame(n/fps).
        return int(self.fps * t + 0.00001)

    def close(self, delete_lastread=True):
        """ 关闭读取器，终止进程（如果仍然打开）。 """
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
    """Finite state ffmpeg `-i` command option file information parser.
    Is designed to parse the output fast, in one loop. Iterates line by
    line of the `ffmpeg -i <filename> [-f null -]` command output changing
    the internal state of the parser.

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

        self._reset_state()

    def _reset_state(self):
        """Reinitializes the state of the parser. Used internally at
        initialization and at the end of the parsing process.
        """
        # could be 2 possible types of metadata:
        #   - file_metadata: Metadata of the container. Here are the tags set
        #     by the user using `-metadata` ffmpeg option
        #   - stream_metadata: Metadata for each stream of the container.
        self._inside_file_metadata = False

        # this state is needed if `duration_tag_separator == "time="` because
        # execution of ffmpeg decoding the whole file using `-f null -` appends
        # to the output the blocks "Stream mapping:" and "Output:", which
        # should be ignored
        self._inside_output = False

        # map from stream type to default stream
        # if a default stream is not indicated, pick the first one available
        self._default_streams = {}

        # current input file, stream and chapter, which will be built at runtime
        self._current_input_file = {"streams": []}
        self._current_stream = None
        self._current_chapter = None

        # resulting data of the parsing process
        self.result = {
            "video_found": False,
            "audio_found": False,
            "metadata": {},
            "inputs": [],
        }

        # keep the value of latest metadata value parsed so we can build
        # at next lines a multiline metadata value
        self._last_metadata_field_added = None

    def parse(self):
        """Parses the information returned by FFmpeg in stderr executing their binary
        for a file with ``-i`` option and returns a dictionary with all data needed
        by MoviePy.
        """
        # chapters by input file
        input_chapters = []

        for line in self.infos.splitlines()[1:]:
            if (
                self.duration_tag_separator == "time="
                and self.check_duration
                and "time=" in line
            ):
                # parse duration using file decodification
                self.result["duration"] = self.parse_duration(line)
            elif self._inside_output or line[0] != " ":
                if self.duration_tag_separator == "time=" and not self._inside_output:
                    self._inside_output = True
                # skip lines like "At least one output file must be specified"
            elif not self._inside_file_metadata and line.startswith("  Metadata:"):
                # enter "  Metadata:" group
                self._inside_file_metadata = True
            elif line.startswith("  Duration:"):
                # exit "  Metadata:" group
                self._inside_file_metadata = False
                if self.check_duration and self.duration_tag_separator == "Duration: ":
                    self.result["duration"] = self.parse_duration(line)

                # parse global bitrate (in kb/s)
                bitrate_match = re.search(r"bitrate: (\d+) k(i?)b/s", line)
                self.result["bitrate"] = (
                    int(bitrate_match.group(1)) if bitrate_match else None
                )

                # parse start time (in seconds)
                start_match = re.search(r"start: (\d+\.?\d+)", line)
                self.result["start"] = (
                    float(start_match.group(1)) if start_match else None
                )
            elif self._inside_file_metadata:
                # file metadata line
                field, value = self.parse_metadata_field_value(line)

                # multiline metadata value parsing
                if field == "":
                    field = self._last_metadata_field_added
                    value = self.result["metadata"][field] + "\n" + value
                else:
                    self._last_metadata_field_added = field
                self.result["metadata"][field] = value
            elif line.lstrip().startswith("Stream "):
                # exit stream "    Metadata:"
                if self._current_stream:
                    self._current_input_file["streams"].append(self._current_stream)

                # get input number, stream number, language and type
                main_info_match = re.search(
                    r"^Stream\s#(\d+):(\d+)(?:\[\w+\])?\(?(\w+)?\)?:\s(\w+):",
                    line.lstrip(),
                )
                (
                    input_number,
                    stream_number,
                    language,
                    stream_type,
                ) = main_info_match.groups()
                input_number = int(input_number)
                stream_number = int(stream_number)
                stream_type_lower = stream_type.lower()

                if language == "und":
                    language = None

                # start builiding the current stream
                self._current_stream = {
                    "input_number": input_number,
                    "stream_number": stream_number,
                    "stream_type": stream_type_lower,
                    "language": language,
                    "default": (stream_type_lower not in self._default_streams)
                    and line.endswith("(default)"),
                }

                # for default streams, set their numbers globally, so it's
                # easy to get without iterating all
                if self._current_stream["default"]:
                    self._default_streams[stream_type_lower] = self._current_stream

                # exit chapter
                if self._current_chapter:
                    input_chapters[input_number].append(self._current_chapter)
                    self._current_chapter = None

                if "input_number" not in self._current_input_file:
                    # first input file
                    self._current_input_file["input_number"] = input_number
                elif self._current_input_file["input_number"] != input_number:
                    # new input file

                    # include their chapters if there are for this input file
                    if len(input_chapters) >= input_number + 1:
                        self._current_input_file["chapters"] = input_chapters[
                            input_number
                        ]

                    # add new input file to result
                    self.result["inputs"].append(self._current_input_file)
                    self._current_input_file = {"input_number": input_number}

                # parse relevant data by stream type
                try:
                    stream_data = self.parse_data_by_stream_type(stream_type, line)
                except NotImplementedError as exc:
                    warnings.warn(
                        f"{str(exc)}\nffmpeg output:\n\n{self.infos}", UserWarning
                    )
                else:
                    self._current_stream.update(stream_data)
            elif line.startswith("    Metadata:"):
                # enter group "    Metadata:"
                continue
            elif self._current_stream:
                # stream metadata line
                if "metadata" not in self._current_stream:
                    self._current_stream["metadata"] = {}

                field, value = self.parse_metadata_field_value(line)

                if self._current_stream["stream_type"] == "video":
                    field, value = self.video_metadata_type_casting(field, value)
                    # ffmpeg 7 now use displaymatrix instead of rotate
                    if field == "rotate":
                        self.result["video_rotation"] = value
                    elif field == "displaymatrix":
                        self.result["video_rotation"] = value

                # multiline metadata value parsing
                if field == "":
                    field = self._last_metadata_field_added
                    value = self._current_stream["metadata"][field] + "\n" + value
                else:
                    self._last_metadata_field_added = field
                self._current_stream["metadata"][field] = value
            elif line.startswith("    Chapter"):
                # Chapter data line
                if self._current_chapter:
                    # there is a previews chapter?
                    if len(input_chapters) < self._current_chapter["input_number"] + 1:
                        input_chapters.append([])
                    # include in the chapters by input matrix
                    input_chapters[self._current_chapter["input_number"]].append(
                        self._current_chapter
                    )

                # extract chapter data
                chapter_data_match = re.search(
                    r"^    Chapter #(\d+):(\d+): start (\d+\.?\d+?), end (\d+\.?\d+?)",
                    line,
                )
                input_number, chapter_number, start, end = chapter_data_match.groups()

                # start building the chapter
                self._current_chapter = {
                    "input_number": int(input_number),
                    "chapter_number": int(chapter_number),
                    "start": float(start),
                    "end": float(end),
                }
            elif self._current_chapter:
                # inside chapter metadata
                if "metadata" not in self._current_chapter:
                    self._current_chapter["metadata"] = {}
                field, value = self.parse_metadata_field_value(line)

                # multiline metadata value parsing
                if field == "":
                    field = self._last_metadata_field_added
                    value = self._current_chapter["metadata"][field] + "\n" + value
                else:
                    self._last_metadata_field_added = field
                self._current_chapter["metadata"][field] = value

        # last input file, must be included in the result
        if self._current_input_file:
            self._current_input_file["streams"].append(self._current_stream)
            # include their chapters, if there are any
            if (
                "input_number" in self._current_input_file
                and len(input_chapters) == self._current_input_file["input_number"] + 1
            ):
                self._current_input_file["chapters"] = input_chapters[
                    self._current_input_file["input_number"]
                ]
            self.result["inputs"].append(self._current_input_file)

        # set any missing default automatically
        for stream in self._current_input_file["streams"]:
            if stream["stream_type"] not in self._default_streams:
                self._default_streams[stream["stream_type"]] = stream
                stream["default"] = True

        # set some global info based on the defaults
        for stream_type_lower, stream_data in self._default_streams.items():
            self.result[f"default_{stream_type_lower}_input_number"] = stream_data[
                "input_number"
            ]
            self.result[f"default_{stream_type_lower}_stream_number"] = stream_data[
                "stream_number"
            ]

            if stream_type_lower == "audio":
                self.result["audio_found"] = True
                self.result["audio_fps"] = stream_data["fps"]
                self.result["audio_bitrate"] = stream_data["bitrate"]
            elif stream_type_lower == "video":
                self.result["video_found"] = True
                self.result["video_size"] = stream_data.get("size", None)
                self.result["video_bitrate"] = stream_data.get("bitrate", None)
                self.result["video_fps"] = stream_data["fps"]
                self.result["video_codec_name"] = stream_data.get("codec_name", None)
                self.result["video_profile"] = stream_data.get("profile", None)

        # some video duration utilities
        if self.result["video_found"] and self.check_duration:
            self.result["video_duration"] = self.result["duration"]
            self.result["video_n_frames"] = int(
                self.result["duration"] * self.result.get("video_fps", 0)
            )
        else:
            self.result["video_n_frames"] = 0
            self.result["video_duration"] = 0.0
        # We could have also recomputed duration from the number of frames, as follows:
        # >>> result['video_duration'] = result['video_n_frames'] / result['video_fps']

        # not default audio found, assume first audio stream is the default
        if self.result["audio_found"] and not self.result.get("audio_bitrate"):
            self.result["audio_bitrate"] = None
            for streams_input in self.result["inputs"]:
                for stream in streams_input["streams"]:
                    if stream["stream_type"] == "audio" and stream.get("bitrate"):
                        self.result["audio_bitrate"] = stream["bitrate"]
                        break

                if self.result["audio_bitrate"] is not None:
                    break

        result = self.result

        # reset state of the parser
        self._reset_state()

        return result

    def parse_data_by_stream_type(self, stream_type, line):
        """Parses data from "Stream ... {stream_type}" line."""
        try:
            return {
                "Audio": self.parse_audio_stream_data,
                "Video": self.parse_video_stream_data,
                "Data": lambda _line: {},
            }[stream_type](line)
        except KeyError:
            raise NotImplementedError(
                f"{stream_type} stream parsing is not supported by moviepy and"
                " will be ignored"
            )

    def parse_audio_stream_data(self, line):
        """Parses data from "Stream ... Audio" line."""
        stream_data = {}
        try:
            stream_data["fps"] = int(re.search(r" (\d+) Hz", line).group(1))
        except (AttributeError, ValueError):
            # AttributeError: 'NoneType' object has no attribute 'group'
            # ValueError: invalid literal for int() with base 10: '<string>'
            stream_data["fps"] = "unknown"
        match_audio_bitrate = re.search(r"(\d+) k(i?)b/s", line)
        stream_data["bitrate"] = (
            int(match_audio_bitrate.group(1)) if match_audio_bitrate else None
        )
        return stream_data

    def parse_video_stream_data(self, line):
        """Parses data from "Stream ... Video" line."""
        stream_data = {}

        try:
            match_video_size = re.search(r" (\d+)x(\d+)[,\s]", line)
            if match_video_size:
                # size, of the form 460x320 (w x h)
                stream_data["size"] = [int(num) for num in match_video_size.groups()]
        except Exception:
            raise IOError(
                (
                    "MoviePy error: failed to read video dimensions in"
                    " file '%s'.\nHere are the file infos returned by"
                    "ffmpeg:\n\n%s"
                )
                % (self.filename, self.infos)
            )

        match_bitrate = re.search(r"(\d+) k(i?)b/s", line)
        stream_data["bitrate"] = int(match_bitrate.group(1)) if match_bitrate else None

        # Get the frame rate. Sometimes it's 'tbr', sometimes 'fps', sometimes
        # tbc, and sometimes tbc/2...
        # Current policy: Trust fps first, then tbr unless fps_source is
        # specified as 'tbr' in which case try tbr then fps

        # If result is near from x*1000/1001 where x is 23,24,25,50,
        # replace by x*1000/1001 (very common case for the fps).

        if self.fps_source == "fps":
            try:
                fps = self.parse_fps(line)
            except (AttributeError, ValueError):
                fps = self.parse_tbr(line)
        elif self.fps_source == "tbr":
            try:
                fps = self.parse_tbr(line)
            except (AttributeError, ValueError):
                fps = self.parse_fps(line)
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
        stream_data["fps"] = fps

        # Try to extract video codec and profile
        main_info_match = re.search(
            r"Video:\s(\w+)?\s?(\([^)]+\))?",
            line.lstrip(),
        )
        if main_info_match is not None:
            (codec_name, profile) = main_info_match.groups()
            stream_data["codec_name"] = codec_name
            stream_data["profile"] = profile

        return stream_data

    def parse_fps(self, line):
        """Parses number of FPS from a line of the ``ffmpeg -i`` command output."""
        return float(re.search(r" (\d+.?\d*) fps", line).group(1))

    def parse_tbr(self, line):
        """Parses number of TBS from a line of the ``ffmpeg -i`` command output."""
        s_tbr = re.search(r" (\d+.?\d*k?) tbr", line).group(1)

        # Sometimes comes as e.g. 12k. We need to replace that with 12000.
        if s_tbr[-1] == "k":
            tbr = float(s_tbr[:-1]) * 1000
        else:
            tbr = float(s_tbr)
        return tbr

    def parse_duration(self, line):
        """Parse the duration from the line that outputs the duration of
        the container.
        """
        try:
            time_raw_string = line.split(self.duration_tag_separator)[-1]
            match_duration = re.search(
                r"([0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9])",
                time_raw_string,
            )
            return convert_to_seconds(match_duration.group(1))
        except Exception:
            raise IOError(
                (
                    "MoviePy error: failed to read the duration of file '%s'.\n"
                    "Here are the file infos returned by ffmpeg:\n\n%s"
                )
                % (self.filename, self.infos)
            )

    def parse_metadata_field_value(
        self,
        line,
    ):
        """Returns a tuple with a metadata field-value pair given a ffmpeg `-i`
        command output line.
        """
        info = line.split(":", 1)
        if len(info) == 2:
            raw_field, raw_value = info
            return (raw_field.strip(" "), raw_value.strip(" "))
        else:
            return ("", "")

    def video_metadata_type_casting(self, field, value):
        """Cast needed video metadata fields to other types than the default str."""
        if field == "rotate":
            return (field, float(value))

        elif field == "displaymatrix":
            match = re.search(r"[-+]?\d+(\.\d+)?", value)
            if match:
                # We must multiply by -1 because displaymatrix return info
                # about how to rotate to show video, not about video rotation
                return (field, float(match.group()) * -1)

        return (field, value)


def ffmpeg_parse_infos(
    filename,
    check_duration=True,
    fps_source="fps",
    decode_file=False,
    print_infos=False,
):
    """
    使用 FFmpeg 获取文件信息。 返回一个包含以下字段的字典：
    
    - ``"duration"``（总时长）
    - ``"metadata"``（元数据）
    - ``"inputs"``（输入文件信息）
    - ``"video_found"``（是否找到视频流）
    - ``"video_fps"``（视频帧率）
    - ``"video_n_frames"``（视频总帧数）
    - ``"video_duration"``（视频时长）
    - ``"video_bitrate"``（视频比特率）
    - ``"video_metadata"``（视频元数据）
    - ``"audio_found"``（是否找到音频流）
    - ``"audio_fps"``（音频采样率）
    - ``"audio_bitrate"``（音频比特率）
    - ``"audio_metadata"``（音频元数据）
    - ``"video_codec_name"``（视频编码格式）
    - ``"video_profile"``（视频编码配置）
    
    请注意，"video_duration" 的值通常比 "duration" 略小，
    这是为了避免读取视频文件尾部的**不完整帧**，因为这样会导致错误。
    
    参数说明
    ----------
    
    filename
      需要解析的文件名，仅用于报错时提供更准确的错误信息。
    
    fps_source
      指定首选的帧率数据来源。
    
    check_duration
      是否启用文件时长解析。对于静态图片，可以跳过该步骤，提高效率。
    
    decode_file
      是否读取整个文件来获取精确的时长信息。
      某些文件（例如 VFR 变帧率视频）可能需要完整解码才能得到正确的时长。
      参考：https://github.com/Zulko/moviepy/pull/1222
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
    except Exception as exc:
        if os.path.isdir(filename):
            raise IsADirectoryError(f"'{filename}' is a directory")
        elif not os.path.exists(filename):
            raise FileNotFoundError(f"'{filename}' not found")
        raise IOError(f"Error passing `ffmpeg -i` command output:\n\n{infos}") from exc
