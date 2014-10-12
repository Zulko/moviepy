.. _effects:

Clips transformations and effects
===================================

There are several categories of clip modifications in MoviePy.

The very common methods for composition (cutting a clip, setting its position, etc.) are implemented as ``clip.mymethod``. For instance ``clip.subclip(15,20)`` returns the part of ``clip`` that is playing between 15 seconds and 20 seconds.

For all the other modifications, we use ``clip.fx`` and ``clip.fl``. ``clip.fx`` is meant to make it easy to use already-written transformation functions, while  ``clip.fl`` makes it easy to write new transformation functions.

Note that none of these methods occur *inplace*: they all create a copy of the clip and let the original clip untouched. Moreover, modified clips are just *special views* of the original clip, they do not carry all the video data with them. Actually, the *real* modifications are only performed when you are rendering the clip (see :ref:`renderingAClip`). This means that all the clip objects that you will create through modifications of other clips take virtually no place in the memory and are created quasi-instantly.

clip.fx
""""""""

Suppose that you have some functions implementing effects on clips: ::
    
    effect_1(clip, args1) -> new clip
    effect_2(clip, args2) -> new clip
    effect_3(clip, args3) -> new clip
    
where ``args`` represent arguments and/or keyword arguments. To apply these functions, in that order, to one clip, you would write something like ::
    
    newclip =  effect_3( effect_2( effect_1(clip, args3), args2), args1) 

but this is not easy to read. To have a clearer syntax you can use ``clip.fx``: ::
    
    newclip = (clip.fx( effect_1, args1)
                   .fx( effect_2, args2)
                   .fx( effect_3, args3))

Much better ! There are already many effects implemented in the modules ``moviepy.video.fx`` and ``moviepy.audio.fx``. The fx methods in these modules are automatically applied to the sound and the mask of the clip if it is relevant, so that you don't have to worry about modifying these. For practicality, when you use ``from moviepy import.editor *``, these two modules are loaded as ``vfx`` and ``afx``, so you may write something like ::
    
    from moviepy.editor import *
    clip = (VideoFileClip("myvideo.avi")
            .fx( vfx.resize, width=460) # resize (keep aspect ratio)
            .fx( vfx.speedx, 2) # double speed
            .fx( vfx.colorx, 0.5)) # darken the picture

For convenience, when you use ``moviepy.editor``, frequently used methods such as ``resize`` can be called in a simpler way: ``clip.resize(...)`` instead of ``clip.fx( vfx.resize, ...)``


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

When programming a new effect, whenever it is possible, prefer using ``fl_time`` and 
``fl_image`` instead of ``fl`` if possible when implementing 
new effects. The reason is that, when these effects are applied to 
ImageClips, MoviePy will recognize that these methods do not need to be applied to each frame, which will 
result in faster renderings.
