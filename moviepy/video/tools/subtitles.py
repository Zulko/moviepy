""" Experimental module for subtitles support. """

import re
import numpy as np
from moviepy.video.VideoClip import VideoClip, TextClip

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
    def __init__(self, subtitles, gen_textclip=None):
        
        VideoClip.__init__(self)

        if isinstance( subtitles, str):
            subtitles = file_to_subtitles(subtitles)
        self.subtitles = subtitles
        self.textclips = dict()
        if gen_textclip is None:
            gen_textclip = lambda txt: TextClip(txt, font='Georgia-Bold',
                                        fontsize=24, color='white',
                                        stroke_color='black', stroke_width=0.5)
        self.gen_textclip = gen_textclip
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
                self.textclips[sub] = gen_textclip(sub[1])
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



def convert_time(timestring):
    """ Converts a string into seconds """
    nums = map(float, re.findall(r'\d+', timestring))
    return 3600*nums[0] + 60*nums[1] + nums[2] + nums[3]/1000



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
        times = re.findall("[0-9]*:[0-9]*:[0-9]*,[0-9]*", line)
        if times != []:
            current_times = map(convert_time, times)
        elif line == '\n':
            times_texts.append((current_times, current_text.strip('\n')))
            current_times, current_text = None, ""
        elif current_times is not None:
            current_text = current_text + line
    
    return times_texts