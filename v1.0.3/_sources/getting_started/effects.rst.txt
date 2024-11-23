.. _effects:

Clips transformations and effects
===================================

There are several categories of clip modifications in MoviePy:

- The very common methods to change the attributes of a clip: ``clip.set_duration``, ``clip.set_audio``, ``clip.set_mask``, ``clip.set_start`` etc.
- The already-implemented effects. Core effects like ``clip.subclip(t1, t2)`` (keep only the cut between t1 and t2), which are very important, are implemented as class methods. More advanced and less common effects like ``loop`` (makes the clip play in a loop) or ``time_mirror`` (makes the clip play backwards) are placed in the special modules ``moviepy.video.fx`` and ``moviepy.audio.fx`` and are applied with the ``clip.fx`` method, for instance ``clip.fx(time_mirror)`` (makes the clip play backwards), ``clip.fx(black_white)`` (turns the clip black and white), etc.
- The effects that you can create yourself. using 

All these effects have in common that they are **not inplace**: they do NOT modify the original clip, instead they create a new clip that is a version of the former with the changes applied. For instance: ::

    my_clip = VideoFileClip("some_file.mp4")
    my_clip.set_start(t=5) # does nothing, changes are lost
    my_new_clip = my_clip.set_start(t=5) # good !

Also, when you write ``clip.resize(width=640)``, it does not immediately applies the effect to all the frames of the clip, but only to the first frame: all the other frames will be resized only when required (that is, when you will write the whole clip to a file of when you will preview it). Said otherwise, creating a new clip is neither time nor memory hungry, all the computations happen during the final rendering.  

Time representations in MoviePy
---------------------------------

Many methods that we will see accept times as arguments. For instance ``clip.subclip(t_start,t_end)`` which cuts the clip between two times. For these methods, times can be represented either in seconds (``t_start=230.54``), as a couple (minutes, seconds) (``t_start=(3,50.54)``), as a triplet (hour, min, sec) (``t_start=(0,3,50.54)``) or as a string (``t_start='00:03:50.54')``).

Most of the time when the times are not provided they are guessed, for instance in ``clip.subclip(t_start=50)`` it is implied that ``t_end`` corresponds to the end of the clip, in ``clip.subclip(t_end=20)`` it is implied that t_start=0. If the time is negative it is considered as the time before the end of the clip: ``clip.subclip(-20, -10)`` cuts the clip between 20s before the end and 10s before the end.


Methods to change the clip attributes
---------------------------------------

clip.fx
----------

Suppose that you have some functions implementing effects on clips, i.e. functions which, given a clip and some arguments, return a new clip: ::
    
    effect_1(clip, args1) -> new clip
    effect_2(clip, args2) -> new clip
    effect_3(clip, args3) -> new clip
    
where ``args`` represent arguments and/or keyword arguments. To apply these functions, in that order, to one clip, you would write something like ::
    
    newclip =  effect_3( effect_2( effect_1(clip, args3), args2), args1) 

but this is not easy to read. To have a clearer syntax you can use ``clip.fx``: ::
    
    newclip = (clip.fx( effect_1, args1)
                   .fx( effect_2, args2)
                   .fx( effect_3, args3))

Much better ! There are already many effects implemented in the modules ``moviepy.video.fx`` and ``moviepy.audio.fx``. The fx methods in these modules are automatically applied to the sound and the mask of the clip if it is relevant, so that you don't have to worry about modifying these. For practicality, when you use ``from moviepy.editor import *``, these two modules are loaded as ``vfx`` and ``afx``, so you may write something like ::
    
    from moviepy.editor import *
    clip = (VideoFileClip("myvideo.avi")
            .fx( vfx.resize, width=460) # resize (keep aspect ratio)
            .fx( vfx.speedx, 2) # double the speed
            .fx( vfx.colorx, 0.5)) # darken the picture

For convenience, when you use ``moviepy.editor``, frequently used methods such as ``resize`` can be called in a simpler way: ``clip.resize(...)`` instead of ``clip.fx( vfx.resize, ...)``


Methods to create custom effects
----------------------------------

clip.fl
""""""""


You can modify a clip as you want using custom *filters* with ``clip.fl_time``, ``clip.fl_image``, and more generally with ``clip.fl``.

You can change the timeline of the clip with ``clip.fl_time`` like this: ::
    
    modifiedClip1 = my_clip.fl_time(lambda t: 3*t)
    modifiedClip2 = my_clip.fl_time(lambda t: 1+sin(t))
     
Now the clip ``modifiedClip1`` plays the same as ``my_clip``, only three times faster, while ``modifiedClip2`` will play ``my_clip`` by oscillating between the times t=0s and t=2s. Note that in the last case you have created a clip of infinite duration (which is not a problem for the moment).

You can also modify the display of a clip with ``clip.fl_image``. The following takes a clip and inverts the green and blue channels of the frames: ::
    
    def invert_green_blue(image):
        return image[:,:,[0,2,1]]
    
    modifiedClip = my_clip.fl_image( invert_green_blue )
    
Finally, you may want to process the clip by taking into account both the time and the frame picture. This is possible with the method ``clip.fl(filter)``. The filter must be a function which takes two arguments and returns a picture. the fist argument is a ``get_frame`` method (i.e. a function ``g(t)`` which given a time returns the clip's frame at that time), and the second argument is the time.  ::
    
    def scroll(get_frame, t):
        """
        This function returns a 'region' of the current frame.
        The position of this region depends on the time.
        """
        frame = get_frame(t)
        frame_region = frame[int(t):int(t)+360,:]
        return frame_region
    
    modifiedClip = my_clip.fl( scroll )

This will scroll down the clip, with a constant height of 360 pixels.

When programming a new effect, whenever it is possible, prefer using ``fl_time`` and ``fl_image`` instead of ``fl`` if possible when implementing new effects. The reason is that, when these effects are applied to 
ImageClips, MoviePy will recognize that these methods do not need to be applied to each frame, which will 
result in faster renderings.
