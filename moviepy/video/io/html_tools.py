"""
This module implements ipython_display
A function to embed images/videos/audio in the IPython Notebook
"""

# Notes:
# All media are physically embedded in the IPython Notebook
# (instead of simple links to the original files)
# That is because most browsers use a cache system and they won't
# properly refresh the media when the original files are changed.

import os
from base64 import b64encode
from moviepy.tools import extensions_dict

try:
    from IPython.display import HTML
    ipython_available = True
except ImportError:
    ipython_available = False

from .ffmpeg_reader import ffmpeg_parse_infos

sorry = "Sorry, seems like your browser doesn't support HTML5 audio/video"
templates = {"audio":("<center><audio controls>"
                         "<source %(options)s  src='data:audio/%(ext)s;base64,%(data)s'>"
                     +sorry+"</audio></center>"),
             "image":"<center><img %(options)s "
                     "src='data:image/%(ext)s;base64,%(data)s'></center>",
             "video":("<center><video %(options)s"
                       "src='data:video/%(ext)s;base64,%(data)s' controls>"
                       +sorry+"</video></center>")}


def html_embed(clip, filetype=None, maxduration=60, rendering_kwargs=None,
                    **html_kwargs):
    """ Returns HTML5 code embedding the clip
    
    clip
      Either a file name, or a clip to preview.
      Either an image, a sound or a video. Clips will actually be
      written to a file and embedded as if a filename was provided.


    filetype:
      One of 'video','image','audio'. If None is given, it is determined
      based on the extension of ``filename``, but this can bug.
    
    **kwargs:
      Allow you to give some options, like width=260, etc.

    Examples
    =========

    >>> import moviepy.editor as mpy
    >>> # later ...
    >>> clip.write_videofile("test.mp4")
    >>> mpy.ipython_display("test.mp4", width=360)

    >>> clip.audio.write_audiofile('test.ogg') # Sound !
    >>> mpy.ipython_display('test.ogg')

    >>> clip.write_gif("test.gif")
    >>> mpy.ipython_display('test.gif')

    >>> clip.save_frame("first_frame.jpeg")
    >>> mpy.ipython_display("first_frame.jpeg")

    """  
    
    if rendering_kwargs is None:
      rendering_kwargs = {}
    # QUICK AND VERY DIRTY: next step is use "isinstance" with classes.
    # But cross-dependencies in modules may make it difficult...
    if "Clip" in str(clip.__class__):
        TEMP_PREFIX = "__temp__"
        if "ImageClip" in str(clip.__class__):
            filename = TEMP_PREFIX+".png"
            kwargs = {'filename':filename}
            kwargs.update(rendering_kwargs)
            clip.save_frame(**kwargs)
        elif "Video" in str(clip.__class__):
            filename = TEMP_PREFIX+".mp4"
            kwargs = {'filename':filename, 'verbose':False, 'preset':'ultrafast'}
            kwargs.update(rendering_kwargs)
            clip.write_videofile(**kwargs)
        elif "AudioClip" in str(clip.__class__):
            filename = TEMP_PREFIX+".mp3"
            kwargs = {'filename': filename, 'verbose':False}
            kwargs.update(rendering_kwargs)
            clip.write_audiofile(filename, **kwargs)
        else:
          raise ValueError("Unknown class for the clip. Cannot embed and preview.")

        return html_embed(filename, maxduration=maxduration, rendering_kwargs=rendering_kwargs,
                                **html_kwargs)
    
    filename = clip
    options = " ".join(["%s='%s'"%(str(k), str(v)) for k,v in html_kwargs.items()])
    name, ext = os.path.splitext(filename)
    ext = ext[1:]

    if filetype is None:
        ext = filename.split('.')[-1].lower()
        if ext == "gif":
            filetype = 'image'
        elif ext in extensions_dict:
            filetype = extensions_dict[ext]['type']
        else:
            raise ValueError("No file type is known for the provided file. Please provide "
                             "argument `filetype` (one of 'image', 'video', 'sound') to the "
                             "ipython display function.")
    
    
    if filetype== 'video':
        # The next lines set the HTML5-cvompatible extension and check that the
        # extension is HTML5-valid
        exts_htmltype = {'mp4': 'mp4', 'webm':'webm', 'ogv':'ogg'}
        allowed_exts = " ".join(exts_htmltype.keys()) 
        try:
            ext = exts_htmltype[ext]
        except:
            raise ValueError("This video extension cannot be displayed in the "
                   "IPython Notebook. Allowed extensions: "+allowed_exts)
    
    if filetype in ['audio', 'video']:

        duration = ffmpeg_parse_infos(filename)['duration']
        if duration > maxduration:
            raise ValueError("The duration of video %s (%.1f) exceeds the 'max_duration' "%(filename, duration)+
                             "attribute. You can increase 'max_duration', "
                             "but note that embedding large videos may take all the memory away !")
            
    with open(filename, "rb") as f:
        data= b64encode(f.read())

    template = templates[filetype]

    return template%{'data':data, 'options':options, 'ext':ext}


def ipython_display(clip, filetype=None, maxduration=60, rendering_kwargs=None,
                    **html_kwargs):
    """
    clip
      Either the name of a file, or a clip to preview. The clip will
      actually be written to a file and embedded as if a filename was provided.


    filetype:
      One of 'video','image','audio'. If None is given, it is determined
      based on the extension of ``filename``, but this can bug.
    
    **kwargs:
      Allow you to give some options, like width=260, etc.
    
    Remarks: If your browser doesn't support HTML5, this should warn you.
    If nothing is displayed, maybe your file or filename is wrong.
    The media will be physically embedded in the notebook.

    Examples
    =========

    >>> import moviepy.editor as mpy
    >>> # later ...
    >>> clip.write_videofile("test.mp4")
    >>> mpy.ipython_display("test.mp4", width=360)

    >>> clip.audio.write_audiofile('test.ogg') # Sound !
    >>> mpy.ipython_display('test.ogg')

    >>> clip.write_gif("test.gif")
    >>> mpy.ipython_display('test.gif')

    >>> clip.save_frame("first_frame.jpeg")
    >>> mpy.ipython_display("first_frame.jpeg")
    """
    if not ipython_available:
        raise ImportError("Only works inside an IPython Notebook")
    return HTML(html_embed(clip, filetype=filetype, maxduration=maxduration,
                rendering_kwargs=rendering_kwargs, **html_kwargs))