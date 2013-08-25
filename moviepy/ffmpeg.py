"""  Very experimental 'bindings' to ffmpeg and ImageMagick."""

import os

def movie_from_frames(filename, folder, fps, digits=6):
    """ Writes a movie out of the frames (picture files) in a folder """
    s = "%" + "%02d" % digits + "d.png"
    cmd = ("ffmpeg -y -f image2 -r %d -i %s/%s" % (fps, folder, folder) +
             s + " -b %dk -r %d %s" % (bitrate, self.fps, filename))
    os.system(cmd)
    return cmd


def extract_subclip(filename, t1, t2, targetname=None):
    """ makes a new video file playing video file ``filename`` between
        the times ``t1`` and ``t2``. """
    name,ext = os.path.splitext(filename)
    if not targetname:
        T1, T2 = [int(1000*t) for t in [t1, t2]]
        targetname = name+ "%sSUB%d_%d.%s"(name, T1, T2, ext)
        
    cmd = ( "ffmpeg -y -ss %0.2f -t %0.2f"%(t1, t2-t1)+
            " -i %s -vcodec copy -acodec copy %s"%(filename, targetname))
    os.system(cmd)
    return cmd
    


def merge_video_audio(video,audio,output):
    """ merges video file ``video`` and audio file ``audio`` into one
        movie file ``output``. """
    cmd = "ffmpeg -y -i %s -i %s -vcodec copy -acodec libvorbis %s"%(
                  audio, video, output)
    print "running:  %s" % cmd
    os.system(cmd)
    return cmd

def gif_to_directory(gif_file,dirName=None):
    """
    Stores all the frames of the given .gif file
    into the directory ``dirName``. If ``dirName``
    is not provided, the directory has the same name
    as the .gif file. Supports transparency.
    Returns the directory name.
    
    Example:

    >>> d = gif_to_directory("animated-earth.gif")
    >>> clip = DirectoryClip(d,fps=3)
        
    """
    
    if dirName is None:
        name, ext = os.path.splitext(gif_file)
        dirName = name
    
    try:
        os.mkdir(dirName)
    except:
        pass
    
    cmd = "convert -coalesce %s %s" %(
            gif_file, os.path.join(dirName,"%04d.png"))
    os.system(cmd)
    return dirName
    
    
def extract_audio(inputfile,output,bitrate=3000,fps=44100):
    """ extract the sound from a video file and save it in ``output`` """
    cmd = "ffmpeg -y -i %s -ab %dk -ar  %d %s"%(inputfile,bitrate,fps,output)
    os.system(cmd)
    return cmd
    
    
def resize(video,output,size):
    """ resizes ``video`` to new size ``size`` and write the result
        in file ``output``. """
    cmd = "ffmpeg -i %s -vf scale=%d:%d %s"%(video,res[0],res[1],output)
    os.system(cmd)
    return cmd
