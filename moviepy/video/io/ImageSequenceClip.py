from ..VideoClip import VideoClip
from .ffmpeg_reader import ffmpeg_read_image
import os

class ImageSequenceClip(VideoClip):
    """
    
    A VideoClip made from a series of images.
    

    Parameters
    -----------

    sequence
      Can be one of these:
      - The name of a folder (containing only pictures). The pictures
        will be considered in alphanumerical order.
      - A list of names of image files.
      - A list of Numpy arrays representing images. In this last case,
        masks are not supported currently.


    fps
      Number of picture frames to read per second.

    with_mask
      Should the alpha layer of PNG images be considered as a mask ?

    ismask
      Will this sequence of pictures be used as an animated mask.

    
    """


    def __init__(self, sequence, fps, with_mask=True, ismask=False):

        # CODE WRITTEN AS IT CAME, MAY BE IMPROVED IN THE FUTURE

        VideoClip.__init__(self, ismask=ismask)

        # Parse the data

        fromfiles = True

        if isinstance(sequence, list):
            if not isinstance(sequence[0], str):
                # sequence is a list of numpy arrays
                fromfiles = False
        else:
            # sequence is a folder name
            sequence = sorted([os.path.join(sequence, f)
                        for f in os.listdir(sequence)])

        self.fps = fps
        self.duration = 1.0* len(sequence) / self.fps
        self.end = self.duration
        self.sequence = sequence

        if fromfiles:

            self.lastpos = None
            self.lastimage = None

            def get_frame(t):
            
                pos = int(self.fps*t)
                if pos != self.lastpos:
                    self.lastimage = ffmpeg_read_image(
                                           self.sequence[pos], 
                                           with_mask=False)
                    self.lastpos = pos
                
                return self.lastimage

            if with_mask and (get_frame(0).shape[2]==4):

                self.mask = VideoClip(ismask=True)

                def mask_get_frame(t):
            
                    pos = int(self.fps*t)
                    if pos != self.lastpos:
                        self.mask.lastimage = ffmpeg_read_image(
                                                self.sequence[pos], 
                                                with_mask=True)[:,:,3]
                    self.mask.lastpos = pos

                    return self.mask.lastimage

                self.mask.get_frame = mask_get_frame
                self.mask.size = mask_get_frame(0).shape[:2][::-1]


        else:

            def get_frame(t):
            
                pos = int(self.fps*t)
                return self.sequence[pos]
        
            
        self.get_frame = get_frame
        self.size = get_frame(0).shape[:2][::-1]
