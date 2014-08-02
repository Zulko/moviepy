.. _crashcourse:

A MoviePy crash-course
-----------------------


This section presents the basics of video editing with MoviePy.


Example code
~~~~~~~~~~~~~~

In a typical MoviePy script, you load some clips from video files, then modify them, put them together, and write the result to a video file. As an example, let us load a movie of my last holidays, lower the volume, add a title in the center of the video for the first ten seconds, and write the result in a file: ::
    
    # Import everything needed to edit video clips
    from moviepy.editor import *
    
    # Load myHolidays.mp4 and select the subclip 00:00:50 - 00:00:60
    clip = VideoFileClip("myHolidays.mp4").subclip(50,60)

    # Reduce the audio volume (volume x 0.8)
    clip = clip.volumex(0.8) 
    
    # Generate a text clip. You can customize the font, color, etc.
    txt_clip = TextClip("My Holidays 2013",fontsize=70,color='white')
    
    # Say that you want it to appear 10s at the center of the screen
    txt_clip = txt_clip.set_pos('center').set_duration(10)
    
    # Overlay the text clip on the first video clip
    video = CompositeVideoClip([clip, txt_clip])
    
    # Write the result to a file
    video.write_videofile("myHolidays_edited.avi",fps=24, codec='mpeg4')


What powers MoviePy
~~~~~~~~~~~~~~~~~~~~~

MoviePy uses the software ``ffmpeg`` to read frames from video and audio files. The code to edit and put these frames together relies mainly on the Python library Numpy. The edited frames are assembled in a video file using once again ``ffmpeg``. The software ImageMagick can also be used to generate texts or export an animation in GIF format.

.. image:: explanations.jpeg
    :width: 570px
    :align: center

The clip objects
~~~~~~~~~~~~~~~~~~~

The most common objects in MoviePy are called clips. A clip (let's call it ``my_clip``) can be either an audio clip or a video clip. It has different attributes, like ``my_clip.duration`` (indicating its duration in seconds), ``clip.start`` (indicating the time in seconds where the clip should start playing when mixed with other videos), ``my_clip.w`` (the width in pixel of the clip), etc.

A video clip ``my_clip`` can have two special attributes which are themselves clips: ``my_clip.audio`` is an audio clip representing the audio track of the vidceo clip. ``my_clip.mask`` is a special kind of video clip which defines the transparency of ``my_clip``.

A clip also has methods which enable to create a derivative of this clip. For instance ``my_clip.subclip(2,7)`` creates a new clip which is like ``my_clip`` cut between seconds 2 and 7. 

Classes of video clips
~~~~~~~~~~~~~~~~~~~~~~

Video clips are the building blocks of longer videos. They can be created with one of the following:

- ``VideoFileClip('myHolidays.mp4')`` will generate a clip from a video file. This video file can have any format or extension : mp4, flv, mov, ... even gif ! 
- ``ImageClip('myPicture.png')`` will generate a clip displaying a picture, for an *a priori* infinite duration.
- ``ColorClip((height,width),color=(R,G,B))`` generates a special ImageClip of a single color.
- ``TextClip('Hello folks !',font='Impact-Regular')`` generates a special ImageClip representing a text. The generation of the text image is made by the software ImageMagick (see the Installation section).

To that list we should add the ``CompositeVideoClips`` which are obtained by putting several clips together.

.. _CompositeVideoClips:

Composite video clips
~~~~~~~~~~~~~~~~~~~~~

Composite video clips are video clips which will display the contents of several other video clips. The simplest compositing is concatenation with :meth:`~moviepy.video.compositing.concatenate.concatenate`: ::
    
    video = concatenate([clip1,clip2,clip3])

Now ``video`` is a clip that plays the clips 1, 2, and 3 one after the other. You can also play a transition clip between the clips with the option ``transition=my_clip``.

Next, you have the `~moviepy.video.compositing.CompositeVideoClip.CompositeVideoClip`: ::
    
    video = CompositeVideoClip([clip1,clip2,clip3])
 
Now ``video`` plays ``clip1``, and ``clip2`` *on top of* ``clip1``, and ``clip3`` on top of ``clip1``, and ``clip2``. For instance, if ``clip2`` and ``clip3`` have the same size as ``clip1``, then only ``clip3``, which is on top, will be visible in the video... unless  ``clip3`` and ``clip2`` have masks which hide parts of them. Note that by default the composition has the size of its first clip (as it is generally a *background*). But sometimes you will want to make your clips *float* in a bigger composition, so you will specify the size of the final composition as follows ::

    video = CompositeVideoClip([clip1,clip2,clip3], size=(720,460))
    
In a CompositionClip, all the clips start to play at a time that is specified by the ``clip.start`` attribute. You can set this starting time as follows: ::
    
    clip1 = clip1.set_start(5) # start after 5 seconds 

So for instance your composition will look like ::

    video = CompositeVideoClip([clip1, # starts at t=0
                                clip2.set_start(5), # start at t=5s
                                clip3.set_start(9)]) # start at t=9s

In the example above, maybe ``clip2`` will start before ``clip1`` is over. In this case you can make ``clip2`` appear with a *fade-in* effect of one second: ::
    
    video = CompositeVideoClip([clip1, # starts at t=0
                                clip2.set_start(5).fadein(1),
                                clip3.set_start(9)])

Finally, if ``clip2`` and ``clip3`` are smaller than ``clip1``, you can decide where they will appear in the composition by setting their position. Here we indicate the coordinates of the top-left pixel: ::
    
    video = CompositeVideoClip([clip1,
                               clip2.set_pos((45,150)),
                               clip3.set_pos((90,100))])

Note that there are many ways to specify the position: ::
    
    clip2.set_pos((45,150)) # x=45, y=150 , in pixels
    
    clip2.set_pos("center") # automatically centered

    # clip2 is horizontally centered, and at the top of the picture
    clip2.set_pos(("center","top"))

    # clip2 is vertically centered, at the left of the picture
    clip2.set_pos(("left","center"))
    
    # clip2 is at 40% of the width, 70% of the height of the screen:
    clip2.set_pos((0.4,0.7), relative=True)
    
    # clip2's position is horizontally centered, and moving down !
    clip2.set_pos(lambda t: ('center', 50+t) )

When indicating the position keep in mind that the ``y`` coordinate has its zero at the top of the picture:

.. figure:: videoWH.jpeg

.. _renderingAClip:

Writing a video clip to a file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To write a clip as a video file, use ::
    
    my_clip.write_videofile("movie.mp4") # default: 'libx264', 24 fps
    my_clip.write_videofile("movie.mp4",fps=15, codec='mpeg4')
    my_clip.write_videofile("movie.mp4",audio=False) # don't render audio.
    
You can also use other codecs to write ``.webm`` or ``.ogv`` files.


Sometimes it is impossible for MoviePy to guess the ``duration`` attribute of the clip (keep in mind that some clips, like ImageClips displaying a picture, have *a priori* an infinite duration). Then, the ``duration`` must be set manually with ``clip.set_duration``: ::

    # Make a video showing a flower for 5 seconds
    my_clip = Image("flower.jpeg") # has infinite duration
    my_clip.write_videofile("flower.mp4") # Will fail ! NO DURATION !
    my_clip.set_duration(5).write_videofile("flower.mp4") # works !


Writing an animated GIF
~~~~~~~~~~~~~~~~~~~~~~~~~

To write your video as an animated GIF, use ::

    my_clip.write_gif('test.gif', fps=12)

If your computer has enough RAM (say, at least 2GB), you can use its faster version ``write_gif2``:

    my_clip.write_gif2('test.gif', fps=12)


See `this blog post <http://zulko.github.io/blog/2014/01/23/making-animated-gifs-from-video-files-with-python>`_ for more informations on making GIFs with MoviePy.

Previewing a video clip
~~~~~~~~~~~~~~~~~~~~~~~

A clip previewed, i.e. generated and displayed at the same time, which is faster than re-generating the file and opening it every time you change your script. Previewing requires to have the Python package PyGame installed, and will only work if PyGame is initialized, which will be the case
if you started with ``from moviepy import *``.

To preview just one frame of the clip, use one of these: ::
    
    my_clip.show() # shows the first frame of the clip
    my_clip.show(10.5) # shows the frame of the clip at t=10.5s
    my_clip.show(interactive = True)

The last line allows you to click anywhere on the clip and get the position and color of the pixel on which you clicked (press Escape to terminate).

To preview the clip, you must specify the frames-per-second ::
    
    my_clip.preview() # preview with default fps=15
    my_clip.preview(fps=25)
    my_clip.preview(fps=15, audio=False) # don't play sound.

The ``fps`` can be any number, independently of the ``fps`` of your different sources.

While the clip is getting prewieved, just can just click anywhere on the clip to get the time, position and color of the pixel you clicked.

.. _CCaudioClips:

Audio clips
~~~~~~~~~~~~~

The second important objects of MoviePy are the audio clips. If ``myHolidays.mp4`` is a video with sound, then ::
    
    clip = VideoFileClip('myHolidays.mp4')

will create a clip with a ``clip.audio`` attribute which is an audio clip. This is the sound that you will hear if you render the clip with ``clip.preview`` or ``clip.write_videofile``. You can also create an audio clip from a sound file and then attach it to a video clip: ::
        
    audio = AudioFileClip('mySong.wav')
    video = VideoFileClip('myHolidays.mp4').set_audio(audio)

Like video clips, audio clips can be cut (with ``clip.subclip``) modified (with for instance ``clip.volumex`` which multiplies the volume) and combined (with ``CompositeAudioClip``). But most of the time, MoviePy will do that for you:

- When you cut a video clip with ``videoclip.subclip(20,25)`` then the sound will also be cut, i.e. the resulting clip will have an audio clip ``videoclip.audio.subclip(20,25)``.
- When you put several clips together in a CompositeVideoClip, then the sound of the CompositeVideoClip will be the composition of the sounds of the different video clips.

For an example, you can refer to :ref:`soundexample`. Like video clips, sound clips have a ``get_frame`` attribute, and creating new audio clips by modifying or putting together other audio clips does not eat the memory. The actual sounds of the audio clips are only computed when we ask to play them or to write them to a file. You can do that as follows: ::
    
    audioclip.preview() # default fps: 22050
    audioclip.preview(fps=44100)
    audioclip.to_audiofile('my_clip.mp3',fps=44100) #default fps: 22050


Operations on a clip
~~~~~~~~~~~~~~~~~~~~~

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

To go further
~~~~~~~~~~~~~~

The best way to start with moviepy is to use it with the IPython Notebook, as it has autocompletion which will help you find all you need and discover all the available methods.

Advanced features of MoviePy that cannot be expressed as an ``fx`` are placed in :module:`moviepy.video.tools` (currently this module contains methods for tracking objects, segmenting, drawing, making credits, dealing with subtitles) and `moviepy.audio.tools` (currently empty, will contain denoisers and utilities for synchronization).

To go further and learn about all the available options and
functionalities of MoviePy, see the :ref:`examples` and the :ref:`reference_manual`.
You can also browse the code of the different video effects in 
``moviepy/video/fx`` to give you ideas on how to code your own effects.