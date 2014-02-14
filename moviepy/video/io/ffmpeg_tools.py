""" Misc. bindings to ffmpeg and ImageMagick."""

import os
import sys
import subprocess as sp


import decorator


@decorator.decorator
def subprocess_call(f, *a, **k):
    """
    executes the outputed subprocess command
    """
    cmd = f(*a, **k)
    sys.stdout.write( "\nRunning:\n>>> "+ " ".join(cmd))
    sys.stdout.flush()
    proc = sp.Popen(cmd, stdout=sp.PIPE, stdin = sp.PIPE, stderr = sp.PIPE)
    proc.wait()
    if proc.returncode:
        sys.stdout.write( "\nWARNING: this command returned an error:")
        sys.stdout.write(proc.stderr.read().decode('utf8'))
    else:
        sys.stdout.write( "\n... ffmpeg command successful.\n")
    sys.stdout.flush()

@subprocess_call
def movie_from_frames(filename, folder, fps, digits=6):
    """ Writes a movie out of the frames (picture files) in a folder """
    s = "%" + "%02d" % digits + "d.png"
    return ["ffmpeg", "-y", "-f","image2",
             "-r", "%d"%fps,
             "-i", os.path.join(folder,folder) + '/' + s,
             "-b", "%dk"%bitrate,
             "-r", "%d"%self.fps,
             filename]

@subprocess_call
def extract_subclip(filename, t1, t2, targetname=None):
    """ makes a new video file playing video file ``filename`` between
        the times ``t1`` and ``t2``. """
    name,ext = os.path.splitext(filename)
    if not targetname:
        T1, T2 = [int(1000*t) for t in [t1, t2]]
        targetname = name+ "%sSUB%d_%d.%s"(name, T1, T2, ext)
    
    return ["ffmpeg","-y",
      "-i", filename,
      "-ss", "%0.2f"%t1,
      "-t", "%0.2f"%(t2-t1),
      "-vcodec", "copy", "-acodec", "copy", targetname]
    

@subprocess_call
def merge_video_audio(video,audio,output, vcodec='copy', acodec='copy',
                       ffmpeg_output=False):
    """ merges video file ``video`` and audio file ``audio`` into one
        movie file ``output``. """
    return ["ffmpeg", "-y", "-i", audio,"-i", video,
             "-vcodec", vcodec, "-acodec", acodec, output]
    
@subprocess_call
def extract_audio(inputfile,output,bitrate=3000,fps=44100):
    """ extract the sound from a video file and save it in ``output`` """
    return ["ffmpeg", "-y", "-i", inputfile, "-ab", "%dk"%bitrate,
         "-ar", "%d"%fps, output]
    
@subprocess_call   
def resize(video,output,size):
    """ resizes ``video`` to new size ``size`` and write the result
        in file ``output``. """
    return ["ffmpeg", "-i", video, "-vf", "scale=%d:%d"%(res[0], res[1]),
             output]

