import os
import numpy as np

from ..VideoClip import VideoClip
from imageio import imread


class ImageSequenceClip(VideoClip):
    """
    
    A VideoClip made from a series of images.
    

    Parameters
    -----------

    sequence
      Can be one of these:
      - The name of a folder (containing only pictures). The pictures
        will be considered in alphanumerical order.
      - A list of names of image files. In this case you can choose to
        load the pictures in memory pictures 
      - A list of Numpy arrays representing images. In this last case,
        masks are not supported currently.

    fps
      Number of picture frames to read per second. Instead, you can provide
      the duration of each image with durations (see below)

    durations
      List of the duration of each picture.

    with_mask
      Should the alpha layer of PNG images be considered as a mask ?

    ismask
      Will this sequence of pictures be used as an animated mask.

    Notes
    ------

    If your sequence is made of image files, the only image kept in 


    
    """


    def __init__(self, sequence, fps=None, durations=None, with_mask=True,
                 ismask=False, load_images=False):

        # CODE WRITTEN AS IT CAME, MAY BE IMPROVED IN THE FUTURE

        VideoClip.__init__(self, ismask=ismask)

        # Parse the data

        fromfiles = True

        if isinstance(sequence, list):
            if isinstance(sequence[0], str):
                if load_images:
                    sequence = [imread(f) for f in sequence]
                    fromfiles = False
                else:
                    fromfiles= True
            else:
                # sequence is already a list of numpy arrays
                fromfiles = False
        else:
            # sequence is a folder name, make it a list of files:
            fromfiles = True
            sequence = sorted([os.path.join(sequence, f)
                        for f in os.listdir(sequence)])

        self.fps = fps
        if fps is not None:
            durations = [1.0/fps for image in sequence]
        self.durations = durations
        self.images_starts = [0]+list(np.cumsum(durations))
        self.duration = sum(durations)
        self.end = self.duration
        self.sequence = sequence
        
        def find_image_index(t):
            return max([i for i in range(len(self.sequence))
                              if self.images_starts[i]<=t])

        if fromfiles:

            self.lastindex = None
            self.lastimage = None

            def make_frame(t):
            
                index = find_image_index(t)

                if index != self.lastindex:
                    self.lastimage = imread(self.sequence[index])[:,:,:3] 
                    self.lastindex = index
                
                return self.lastimage

            if with_mask and (make_frame(0).shape[2]==4):

                self.mask = VideoClip(ismask=True)

                def mask_make_frame(t):
            
                    index = find_image_index(t)
                    if index != self.lastindex:
                        self.mask.lastimage = imread(self.sequence[index])[:,:,3]
                    self.mask.lastindex = index

                    return self.mask.lastimage

                self.mask.make_frame = mask_make_frame
                self.mask.size = mask_make_frame(0).shape[:2][::-1]


        else:

            def make_frame(t):
            
                index = find_image_index(t)
                return self.sequence[index]
        
            
        self.make_frame = make_frame
        self.size = make_frame(0).shape[:2][::-1]
