from moviepy.video.VideoClip import VideoClip
from .ffmpeg_reader import ffmpeg_read_image

class DirectoryClip(VideoClip):
    """
    
    A VideoClip read from a directory containing pictures.
    
    """

    def __init__(self, foldername, fps, withmask=True, ismask=False):

        VideoClip.__init__(self, ismask=ismask)

        self.directory = foldername
        self.fps = fps
        self.imagefiles = sorted(os.listdir(foldername))
        
        self.duration = 1.0* len(self.imagefiles) / self.fps
        self.end = self.duration
        
        self.lastpos = None
        self.lastimage = None
        
        
        
        def get_frame(t):
            
            pos = int(self.fps*t)
            if pos != self.lastpos:
                self.lastimage = ffmpeg_read_image(self.imagefiles[ind], 
                                                    withmask=withmask)
                self.lastpos = pos
            
            return self.lastimage
            
        self.get_frame = get_frame
        self.size = get_frame(0).shape[:2][::-1]
