"""Miscellaneous bindings to ffmpeg."""

import os

from moviepy.config import FFMPEG_BINARY
from moviepy.decorators import convert_parameter_to_seconds, convert_path_to_string
from moviepy.tools import ffmpeg_escape_filename, subprocess_call


@convert_path_to_string(("inputfile", "outputfile"))
@convert_parameter_to_seconds(("start_time", "end_time"))
def ffmpeg_extract_subclip(
    inputfile, start_time, end_time, outputfile=None, logger="bar"
):
    """Makes a new video file playing video file between two times.

    Parameters
    ----------

    inputfile : str
      Path to the file from which the subclip will be extracted.

    start_time : float
      Moment of the input clip that marks the start of the produced subclip.

    end_time : float
      Moment of the input clip that marks the end of the produced subclip.

    outputfile : str, optional
      Path to the output file. Defaults to
      ``<inputfile_name>SUB<start_time>_<end_time><ext>``.
    """
    if not outputfile:
        name, ext = os.path.splitext(inputfile)
        t1, t2 = [int(1000 * t) for t in [start_time, end_time]]
        outputfile = "%sSUB%d_%d%s" % (name, t1, t2, ext)

    cmd = [
        FFMPEG_BINARY,
        "-y",
        "-ss",
        "%0.2f" % start_time,
        "-i",
        ffmpeg_escape_filename(inputfile),
        "-t",
        "%0.2f" % (end_time - start_time),
        "-map",
        "0",
        "-vcodec",
        "copy",
        "-acodec",
        "copy",
        "-copyts",
        ffmpeg_escape_filename(outputfile),
    ]
    subprocess_call(cmd, logger=logger)


@convert_path_to_string(("videofile", "audiofile", "outputfile"))
def ffmpeg_merge_video_audio(
    videofile,
    audiofile,
    outputfile,
    video_codec="copy",
    audio_codec="copy",
    logger="bar",
):
    """Merges video file and audio file into one movie file.

    Parameters
    ----------

    videofile : str
      Path to the video file used in the merge.

    audiofile : str
      Path to the audio file used in the merge.

    outputfile : str
      Path to the output file.

    video_codec : str, optional
      Video codec used by FFmpeg in the merge.

    audio_codec : str, optional
      Audio codec used by FFmpeg in the merge.
    """
    cmd = [
        FFMPEG_BINARY,
        "-y",
        "-i",
        ffmpeg_escape_filename(audiofile),
        "-i",
        ffmpeg_escape_filename(videofile),
        "-vcodec",
        video_codec,
        "-acodec",
        audio_codec,
        ffmpeg_escape_filename(outputfile),
    ]

    subprocess_call(cmd, logger=logger)


@convert_path_to_string(("inputfile", "outputfile"))
def ffmpeg_extract_audio(inputfile, outputfile, bitrate=3000, fps=44100, logger="bar"):
    """Extract the sound from a video file and save it in ``outputfile``.

    Parameters
    ----------

    inputfile : str
      The path to the file from which the audio will be extracted.

    outputfile : str
      The path to the file to which the audio will be stored.

    bitrate : int, optional
      Bitrate for the new audio file.

    fps : int, optional
      Frame rate for the new audio file.
    """
    cmd = [
        FFMPEG_BINARY,
        "-y",
        "-i",
        ffmpeg_escape_filename(inputfile),
        "-ab",
        "%dk" % bitrate,
        "-ar",
        "%d" % fps,
        ffmpeg_escape_filename(outputfile),
    ]
    subprocess_call(cmd, logger=logger)


@convert_path_to_string(("inputfile", "outputfile"))
def ffmpeg_resize(inputfile, outputfile, size, logger="bar"):
    """Resizes a file to new size and write the result in another.

    Parameters
    ----------

    inputfile : str
      Path to the file to be resized.

    outputfile : str
      Path to the output file.

    size : list or tuple
      New size in format ``[width, height]`` for the output file.
    """
    cmd = [
        FFMPEG_BINARY,
        "-i",
        ffmpeg_escape_filename(inputfile),
        "-vf",
        "scale=%d:%d" % (size[0], size[1]),
        ffmpeg_escape_filename(outputfile),
    ]

    subprocess_call(cmd, logger=logger)


@convert_path_to_string(("inputfile", "outputfile", "output_dir"))
def ffmpeg_stabilize_video(
    inputfile, outputfile=None, output_dir="", overwrite_file=True, logger="bar"
):
    """
    Stabilizes ``filename`` and write the result to ``output``.

    Parameters
    ----------

    inputfile : str
      The name of the shaky video.

    outputfile : str, optional
      The name of new stabilized video. Defaults to appending '_stabilized' to
      the input file name.

    output_dir : str, optional
      The directory to place the output video in. Defaults to the current
      working directory.

    overwrite_file : bool, optional
      If ``outputfile`` already exists in ``output_dir``, then overwrite
      ``outputfile`` Defaults to True.
    """
    if not outputfile:
        without_dir = os.path.basename(inputfile)
        name, ext = os.path.splitext(without_dir)
        outputfile = f"{name}_stabilized{ext}"

    outputfile = os.path.join(output_dir, outputfile)
    cmd = [
        FFMPEG_BINARY,
        "-i",
        ffmpeg_escape_filename(inputfile),
        "-vf",
        "deshake",
        ffmpeg_escape_filename(outputfile),
    ]

    if overwrite_file:
        cmd.append("-y")

    subprocess_call(cmd, logger=logger)
