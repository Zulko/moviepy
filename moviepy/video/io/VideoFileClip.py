import os

from moviepy.video.VideoClip import VideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.Clip import Clip
from moviepy.video.io.ffmpeg_reader import FFMPEG_VideoReader

class VideoFileClip(VideoClip):

    """
    
    A video clip originating from a movie file. For instance:
    
    >>> clip = VideofileClip("myHolidays.mp4")
    >>> clip2 = VideofileClip("myMaskVideo.avi",ismask = True)
    
    :param filename: Any video file: .ogv, .mp4, .mpeg, .avi, .mov etc.
    :param ismask: `True` if the clip is a mask.
    :param has_mask: 'True' if there is a mask included in the videofile.
       Commonly, video files don't have mask, but you can save the mask
       for the videos that you make with MoviePy (see the doc from
       ``VideoClip.to_videofile`` for more details).
    :param audio: If `True`, then the audio is extracted from the video
                  file, in wav format, and it attributed to the clip.
    
    :ivar filename: Name of the original video file
    :ivar fps: Frames per second in the original file. 
        
    """

    def __init__(self, filename, ismask=False, has_mask=False,
                 audio=True, audio_buffersize = 200000,
                 audio_fps=44100, audio_nbytes=2, verbose=False):
        
        VideoClip.__init__(self, ismask)
        
        # We store the construction parameters in case we need to make
        # a copy (a 'co-reader').
        
        self.parameters = {'filename':filename, 'ismask':ismask,
                           'has_mask':has_mask, 'audio':audio,
                           'audio_buffersize':audio_buffersize}
        
        # Make a reader
        pix_fmt= "rgba" if has_mask else "rgb24"
        self.reader = FFMPEG_VideoReader(filename, pix_fmt=pix_fmt)
        
        # Make some of the reader's attributes accessible from the clip
        self.duration = self.reader.duration
        self.end = self.reader.duration
        
        self.fps = self.reader.fps
        self.size = self.reader.size
        self.get_frame = lambda t: self.reader.get_frame(t)
        
        # Make a reader for the audio, if any.
        if audio:
            self.audio = AudioFileClip(filename,
                                       buffersize= audio_buffersize,
                                       fps = audio_fps,
                                       nbytes = audio_nbytes)
    
    def coreader(self, audio=True):
        """ Returns a copy of the AudioFileClip, i.e. a new entrance point
            to the video file. Use copy when you have different clips
            watching the same video file at different times. """
        return VideoFileClip(**self.parameters)
