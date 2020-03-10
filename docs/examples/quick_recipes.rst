Quick recipes
===============


 
Effects and filters
---------------------

Blurring all frames of a video
"""""""""""""""""""""""""""""""

::

    from skimage.filters import gaussian_filter
    from moviepy.editor import VideoFileClip

    def blur(image):
        """ Returns a blurred (radius=2 pixels) version of the image """
        return gaussian_filter(image.astype(float), sigma=2)
    
    clip = VideoFileClip("my_video.mp4")
    clip_blurred = clip.fl_image( blur )
    clip_blurred.write_videofile("blurred_video.mp4")



Cutting videos
---------------

Scene detection
----------------


Compositing videos
-------------------

Add a title before a video
"""""""""""""""""""""""""""


Art of Gif-making
-------------------

  clip.fx( vfx.time_symmetrize)


    # find a subclip
    T = clip

Useless but fun
----------------


Getting the average frame of a video
"""""""""""""""""""""""""""""""""""""
::

    from moviepy.editor import VideoFileClip, ImageClip
    clip = VideoFileClip("video.mp4")
    fps= 1.0 # take one frame per second
    nframes = clip.duration*fps # total number of frames used
    total_image = sum(clip.iter_frames(fps,dtype=float,logger='bar'))
    average_image = ImageClip(total_image/ nframes)
    average_image.save_frame("average_test.png")

