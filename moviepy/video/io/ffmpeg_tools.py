""" Misc. bindings to ffmpeg and ImageMagick."""

import os

from moviepy.config import FFMPEG_BINARY
from moviepy.decorators import convert_path_to_string
from moviepy.tools import subprocess_call


@convert_path_to_string("filename")
def ffmpeg_movie_from_frames(filename, folder, fps, digits=6, bitrate="v"):
    """
    Writes a movie out of the frames (picture files) in a folder.
    Almost deprecated.
    """
    s = "%" + "%02d" % digits + "d.png"
    cmd = [
        FFMPEG_BINARY,
        "-y",
        "-f",
        "image2",
        "-r",
        "%d" % fps,
        "-i",
        os.path.join(folder, folder) + "/" + s,
        "-b",
        "%dk" % bitrate,
        "-r",
        "%d" % fps,
        filename,
    ]

    subprocess_call(cmd)


@convert_path_to_string(("filename", "targetname"))
def ffmpeg_extract_subclip(filename, t1, t2, targetname=None):
    """Makes a new video file playing video file ``filename`` between
    the times ``t1`` and ``t2``."""
    name, ext = os.path.splitext(filename)
    if not targetname:
        T1, T2 = [int(1000 * t) for t in [t1, t2]]
        targetname = "%sSUB%d_%d%s" % (name, T1, T2, ext)

    cmd = [
        FFMPEG_BINARY,
        "-y",
        "-ss",
        "%0.2f" % t1,
        "-i",
        filename,
        "-t",
        "%0.2f" % (t2 - t1),
        "-map",
        "0",
        "-vcodec",
        "copy",
        "-acodec",
        "copy",
        "-copyts",
        targetname,
    ]
    subprocess_call(cmd)


@convert_path_to_string(("video", "audio", "output"))
def ffmpeg_merge_video_audio(
    video,
    audio,
    output,
    vcodec="copy",
    acodec="copy",
    ffmpeg_output=False,
    logger="bar",
):
    """merges video file ``video`` and audio file ``audio`` into one
    movie file ``output``."""
    cmd = [
        FFMPEG_BINARY,
        "-y",
        "-i",
        audio,
        "-i",
        video,
        "-vcodec",
        vcodec,
        "-acodec",
        acodec,
        output,
    ]

    subprocess_call(cmd, logger=logger)


@convert_path_to_string(("inputfile", "output"))
def ffmpeg_extract_audio(inputfile, output, bitrate=3000, fps=44100):
    """ extract the sound from a video file and save it in ``output`` """
    cmd = [
        FFMPEG_BINARY,
        "-y",
        "-i",
        inputfile,
        "-ab",
        "%dk" % bitrate,
        "-ar",
        "%d" % fps,
        output,
    ]
    subprocess_call(cmd)


@convert_path_to_string(("video", "output"))
def ffmpeg_resize(video, output, size):
    """resizes ``video`` to new size ``size`` and write the result
    in file ``output``."""
    cmd = [
        FFMPEG_BINARY,
        "-i",
        video,
        "-vf",
        "scale=%d:%d" % (size[0], size[1]),
        output,
    ]

    subprocess_call(cmd)


@convert_path_to_string(("inputfile", "outputfile", "output_dir"))
def ffmpeg_stabilize_video(
    inputfile, outputfile=None, output_dir="", overwrite_file=True
):
    """
    Stabilizes ``filename`` and write the result to ``output``.

    Parameters
    -----------

    inputfile
      The name of the shaky video

    outputfile
      The name of new stabilized video
      Optional: defaults to appending '_stabilized' to the input file name

    output_dir
      The directory to place the output video in
      Optional: defaults to the current working directory

    overwrite_file
      If ``outputfile`` already exists in ``output_dir``, then overwrite ``outputfile``
      Optional: defaults to True
    """
    if not outputfile:
        without_dir = os.path.basename(inputfile)
        name, ext = os.path.splitext(without_dir)
        outputfile = f"{name}_stabilized{ext}"

    outputfile = os.path.join(output_dir, outputfile)
    cmd = [FFMPEG_BINARY, "-i", inputfile, "-vf", "deshake", outputfile]
    if overwrite_file:
        cmd.append("-y")
    subprocess_call(cmd)
