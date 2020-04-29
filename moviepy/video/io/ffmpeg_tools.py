""" Misc. bindings to ffmpeg and ImageMagick."""

import os

from moviepy.config import FFMPEG_BINARY
from moviepy.decorators import convert_path_to_string
from moviepy.tools import subprocess_call


@convert_path_to_string(("inputfile", "outputfile"))
def ffmpeg_extract_subclip(
    inputfile, start_time, end_time, outputfile=None, logger="bar"
):
    """ Makes a new video file playing video file ``inputfile`` between
        the times ``start_time`` and ``end_time``. """
    name, ext = os.path.splitext(inputfile)
    if not outputfile:
        T1, T2 = [int(1000 * t) for t in [start_time, end_time]]
        outputfile = "%sSUB%d_%d.%s" % (name, T1, T2, ext)

    cmd = [
        FFMPEG_BINARY,
        "-y",
        "-ss",
        "%0.2f" % start_time,
        "-i",
        inputfile,
        "-t",
        "%0.2f" % (end_time - start_time),
        "-map",
        "0",
        "-vcodec",
        "copy",
        "-acodec",
        "copy",
        outputfile,
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
    """ Merges video file ``videofile`` and audio file ``audiofile`` into one
        movie file ``outputfile``. """
    cmd = [
        FFMPEG_BINARY,
        "-y",
        "-i",
        audiofile,
        "-i",
        videofile,
        "-vcodec",
        video_codec,
        "-acodec",
        audio_codec,
        outputfile,
    ]

    subprocess_call(cmd, logger=logger)


@convert_path_to_string(("inputfile", "outputfile"))
def ffmpeg_extract_audio(inputfile, outputfile, bitrate=3000, fps=44100, logger="bar"):
    """ Extract the sound from a video file and save it in ``outputfile`` """
    cmd = [
        FFMPEG_BINARY,
        "-y",
        "-i",
        inputfile,
        "-ab",
        "%dk" % bitrate,
        "-ar",
        "%d" % fps,
        outputfile,
    ]
    subprocess_call(cmd, logger=logger)


@convert_path_to_string(("inputfile", "outputfile"))
def ffmpeg_resize(inputfile, outputfile, size, logger="bar"):
    """ resizes ``inputfile`` to new size ``size`` and write the result
        in file ``outputfile``. """
    cmd = [
        FFMPEG_BINARY,
        "-i",
        inputfile,
        "-vf",
        "scale=%d:%d" % (size[0], size[1]),
        outputfile,
    ]

    subprocess_call(cmd, logger=logger)
