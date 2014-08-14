""" Experimental module for subtitles support. """

import re
import numpy as np
from moviepy.video.VideoClip import VideoClip, TextClip
from moviepy.tools import cvsecs


class SubtitlesClip(VideoClip):
    """ A Clip that serves as "subtitle track" in videos.
    
    One particularity of this class is that the images of the
    subtitle texts are not generated beforehand, but only if
    needed.

    Parameters
    ==========

    subtitles
      Either the name of a file, or a list

    Examples
    =========
    
    >>> from moviepy.video.tools.subtitles import SubtitlesClip
    >>> from moviepy.video.io.VideoFileClip import VideoFileClip
    >>> generator = lambda txt: TextClip(txt, font='Georgia-Regular',
                                        fontsize=24, color='white')
    >>> sub = SubtitlesClip("subtitles.srt", generator)
    >>> myvideo = VideoFileClip("myvideo.avi")
    >>> final = CompositeVideoClip([clip, subtitles])
    >>> final.to_videofile("final.mp4", fps=myvideo.fps)
    
    """

    def __init__(self, subtitles, make_textclip=None):
        
        VideoClip.__init__(self)

        if isinstance( subtitles, str):
            subtitles = file_to_subtitles(subtitles)

        subtitles = [(map(cvsecs, tt),txt) for tt, txt in subtitles]
        self.subtitles = subtitles
        self.textclips = dict()

        if make_textclip is None:

            make_textclip = lambda txt: TextClip(txt, font='Georgia-Bold',
                                        fontsize=24, color='white',
                                        stroke_color='black', stroke_width=0.5)

        self.make_textclip = make_textclip
        self.start=0
        self.duration = max([tb for ((ta,tb), txt) in self.subtitles])
        self.end=self.duration
        
        def add_textclip_if_none(t):
            sub =[((ta,tb),txt) for ((ta,tb),txt) in self.textclips.keys()
                   if (ta<=t<tb)]
            if sub == []:
                sub = [((ta,tb),txt) for ((ta,tb),txt) in self.subtitles if
                       (ta<=t<tb)]
                if sub == []:
                    return False
            sub = sub[0]
            if sub not in self.textclips.keys():
                self.textclips[sub] = self.make_textclip(sub[1])
            return sub

        def get_frame(t):
            sub = add_textclip_if_none(t)
            return (self.textclips[sub].get_frame(t) if sub
                    else np.array([[[0,0,0]]]))

        def mask_get_frame(t):
            sub = add_textclip_if_none(t)
            return (self.textclips[sub].mask.get_frame(t) if sub
                    else np.array([[0]]))
        
        self.get_frame = get_frame
        self.mask = VideoClip(ismask=True, get_frame=mask_get_frame)
    


    def __iter__(self):
        return self.subtitles.__iter__()
    


    def __getitem__(self, k):
        return self.subtitles[k]

    

    def __str__(self):

        def to_srt(sub_element):
            (ta, tb), txt = sub_element
            fta, ftb = map(time_to_string, (ta, tb))
            return "%s - %s\n%s"%(fta, ftb, txt)
        
        return "\n\n".join(map(to_srt, self.subtitles))
    


    def match_expr(self, expr):

        return SubtitlesClip([e for e in self.subtitles
                              if re.find(expr, e) != []])
    

    def write_srt(self, filename):
        with open(filename, 'w+') as f:
            f.write(str(self))

def file_to_subtitles(filename):
    """ Converts a srt file into subtitles.

    The returned list is of the form ``[((ta,tb),'some text'),...]``
    and can be fed to SubtitlesClip.

    Only works for '.srt' format for the moment.
    """

    with open(filename,'r') as f:
        lines = f.readlines()

    times_texts = []
    current_times , current_text = None, ""
    
    for line in lines:
        times = re.findall("([0-9]*:[0-9]*:[0-9]*,[0-9]*)", line)
        if times != []:
            current_times = map(cvsecs, times)
        elif line == '\n':
            times_texts.append((current_times, current_text.strip('\n')))
            current_times, current_text = None, ""
        elif current_times is not None:
            current_text = current_text + line
    return times_texts