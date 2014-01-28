A MoviePy crash-course
-----------------------

In this section we will give you the basics to start editing your videos.

Example code
~~~~~~~~~~~~~~

In a typical script, you load or generate some clips, modify them, combine them, and write the result to a video file.
So let us load a movie of my last holidays, lower the volume, add a title in the center of the video for the ten first seconds, and write the result in a file: ::
    
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
    video.to_videofile("myHolidays_edited.avi",fps=24, codec='mpeg4')

Classes of video clips
~~~~~~~~~~~~~~~~~~~~~~

Video clips are the building blocks of longer videos. They can be created with one of the following:

- ``VideoFileClip('myHolidays.mp4')`` for clips read from a movie file. See :class:`~moviepy.video.io.VideoFileClip.VideoFileClip`.
- ``ImageClip('myPic.png')`` for clips displaying a picture, for an *a priori* infinite duration. See :class:`~moviepy.video.ImageClip.ImageClip`.
- ``ColorClip((height,width),color=(R,G,B))`` for special ImageClips of a single color. See :class:`~moviepy.video.ImageClip.ColorClip`.
- ``TextClip('Hello folks !',font='Impact-Regular')`` for special ImageClips representing a text. They are automatically generated using ImageMagick. See :class:`~moviepy.video.ImageClip.TextClip`.

To that list we should add the ``CompositeVideoClips`` that are obtained by mixing several clips together.

.. _CompositeVideoClips:

Composite video clips
~~~~~~~~~~~~~~~~~~~~~

Composite video clips are video clips which will display the contents of several other video clips. The simplest compositing is concatenation with :meth:`~moviepy.video.compositing.concatenate.concatenate`: ::
    
    video = concatenate([clip1,clip2,clip3])

Now ``video`` is a clip that plays the clips 1, 2, and 3 one after the other. You can also play a transition clip between the clips with the option ``transition=myClip``.

Next, you have the `~moviepy.video.compositing.CompositeVideoClip.CompositeVideoClip`: ::
    
    video = CompositeVideoClip([clip1,clip2,clip3])
 
Now ``video`` plays ``clip1``, and ``clip2`` *on top of* ``clip1``, and ``clip3`` on top of ``clip1``, and ``clip2``. For instance, if ``clip2`` and ``clip3`` have the same size as ``clip1``, then only ``clip3``, which is on top, will be visible in the video... unless  ``clip3`` and ``clip2`` have masks which hide parts of them. Note that by default the composition has the size of its first clip (as it is generally a *background*). But sometimes you will want to make your clips *float* in a bigger composition, so you will specify the size of the final composition as follows ::

    video = CompositeVideoClip([clip1,clip2,clip3], size=(720,460))
    
In a CompositionClip, all the clips start to play at a time that is specified by the ``clip.start`` attribute. You can set this starting time as follows: ::
    
    clip2 = clip1.set_start(5) # start after 5 seconds 

So for instance your composition will look like ::

    video = CompositeVideoClip([clip1, # starts at t=0
                                clip2.set_start(5), # start at t=5s
                                clip3.set_start(9)]) # start at t=9s

Because the three clips overlap, we can make them appear with a fading-in effect. Here we go for fadein effects that last 1.5 seconds: ::
    
    video = CompositeVideoClip([clip1, # starts at t=0
                                clip2.set_start(50).fadein(1.5),
                                clip3.set_start(90).fadein(1.5)])

Finally, if ``clip2`` and ``clip3`` are smaller than ``clip1``, you can decide where they will appear in the composition: ::
    
    video = CompositeVideoClip([clip1,
                               clip2.set_pos((45,150)),
                               clip3.set_pos((90,100))])

Note that there are many ways to specify the position: ::
    
    clip2.set_pos((45,150)) # x=45, y=150
    
    # clip2 is horizontally centered, and at the top of the picture
    clip2.set_pos(("center","top"))
    
    # clip2 is at 40% of the width, 70% of the height:
    clip2.set_pos((0.4,0.7), relative=True)
    
    # clip2's position is horizontally centered, and moving down !
    clip2.set_pos(lambda t: ('center', 50+t) )

Be careful when indicating the position that the ``y`` position has its zero at the top of the picture:

.. figure:: videoWH.jpeg

.. _renderingAClip:

Rendering a video clip
~~~~~~~~~~~~~~~~~~~~~~~

To preview one frame of the clip, use one of these: ::
    
    myClip.show() # shows the first frame of the clip
    myClip.show(10.5) # shows the frame of the clip at t=10.5s
    myClip.show(10.5,frontend="matplotlib") # show in a matplotlib window

To preview the clip, you type ::
    
    myClip.preview() # preview with default fps=15
    myClip.preview(fps=25)
    myClip.preview(fps=15, audio=False) # Play the clip with no sound.

Note that the ``fps`` can be any number, independently of the ``fps`` of your different sources.

To write a clip as a video file, use ::
    
    myClip.to_videofile("myEditedMovie.avi") # default: codec 'libx264' fps 24
    myClip.to_videofile("myEditedMovie.avi",fps=15, codec='mpeg4')
    myClip.to_videofile("myEditedMovie.avi",audio=False) # don't render the audio.


Sometimes it is impossible for MoviePy to guess the ``duration`` attribute of the clip (keep in mind that some clips, like ImageClips displaying a picture, have *a priori* an infinite duration). Then, the ``duration`` must be set manually with ``clip.set_duration``: ::

    myClip = Image("flower.jpeg") # has infinite duration
    Image("flower.jpeg").preview() # Will fail ! NO DURATION !
    myClip.set_duration(5).preview() # will show flowers for 5 seconds

.. _CCaudioClips:

Audio clips
~~~~~~~~~~~~~

The second important objects of MoviePy are the audio clips. If ``myHolidays.mp4`` is a video with sound, then ::
    
    clip = VideoFileClip('myHolidays.mp4', audio=True)

will create a clip with a ``clip.audio`` attribute which is an audio clip. This is the sound that you will hear if you render the clip with ``clip.preview`` or ``clip.to_videofile``. You can also create an audio clip from a sound file and then attach it to a video clip: ::
        
    audio = AudioFileClip('mySong.wav')
    video = VideoFileClip('myHolidays.mp4').set_audio(audio)

Like video clips, audio clips can be cut (with ``clip.subclip``) modified (with for instance ``clip.volumex`` which multiplies the volume) and combined (with ``CompositeAudioClip``). But most of the time, MoviePy will do that for you:

- When you cut a video clip with ``videoclip.subclip(20,25)`` then the sound will also be cut, i.e. the resulting clip will have an audio clip ``videoclip.audio.subclip(20,25)``.
- When you put several clips together in a CompositeVideoClip, then the sound of the CompositeVideoClip will be the composition of the sounds of the different video clips.

For an example, you can refer to :ref:`soundexample`. Like video clips, sound clips have a ``get_frame`` attribute, and creating new audio clips by modifying or putting together other audio clips does not take place in the memory. The actual sounds of the audio clips are only computed when we ask to play them or to write them to a file. You can do that as follows: ::
    
    audioclip.preview() # default fps: 22050
    audioclip.preview(fps=44100)
    audioclip.to_soundfile('myclip.wav',fps=44100) #default fps: 22050

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
    
    newclip = clip.fx( effect_1, args1).\
                   fx( effect_2, args2).\
                   fx( effect_3, args3)

Much better ! There are already many effects implemented in the modules ``moviepy.video.fx`` and ``moviepy.audio.fx``. The fx methods in these modules are automatically applied to the sound and the mask of the clip if it is relevant, so that you don't have to worry about modifying these. For practicality, when you use ``from moviepy import.all *``, these two modules are loaded as ``vfx`` and ``afx``, so you may write something like ::
    
    from moviepy import.all *
    clip = VideoFileClip("myvideo.avi").\
               fx( vfx.resize, width=460).\ # resize (keep aspect ratio)
               fx( vfx.speedx, 2).\ # double speed
               fx( vfx.colorx, 0.5) # darken (decreases the RGB values)

For convenience, frequently used methods such as ``resize`` can be called in a simpler way: ``clip.resize(...)`` instead of ``clip.fx( vfx.resize, ...)``


clip.fl
""""""""


You can modify a clip as you want using custom *filters* with ``clip.fl_time``, ``clip.fl_image``, and more generally with ``clip.fl``.

You can change the timeline of the clip with ``clip.fl_time`` like this: ::
    
    modifiedClip1 = myClip.fl_time(lambda t: 3*t)
    modifiedClip2 = myClip.fl_time(lambda t: 1+sin(t))
     
Now the clip ``modifiedClip1`` plays the same as ``myClip``, only three times faster, while ``modifiedClip2`` will play ``myClip`` by oscillating between the times t=0s and t=2s. Note that in the last case you have created a clip of infinite duration (which is not a problem for the moment).

You can also modify the display of a clip with ``clip.fl_image``. The following takes a clip and inverts the green and blue channels: ::
    
    modifiedClip = myClip.fl_image(lambda image: image[:,:,[0,2,1]])
    
Finally, you may want to process the clip by taking into account the time and the picture at the same time. This is possible with ``clip.fl``. The filter must be a function which takes two arguments and returns a picture. the fist argument is a ``get_frame`` method (i.e. a function ``g(t)`` which given a time returns the clip's frame at that time), and the second argument is the time.  ::
    
    modifiedClip = myClip.fl(lambda gf,t: gf(t)[int(t):int(t)+360,:]

This will scroll down the clip with a constant height of 360 pixels.

Prefer using ``fl_time`` and ``fl_image`` if possible when implementing new effects. The reason is that for image clips MoviePy will recognize that these methods do not need to be applied to each frames, which will result in shorter computation times.

Tools
~~~~~~

Advanced features of MoviePy that cannot be expressed as an ``fx`` are placed in :module:`moviepy.video.tools` (currently this module contains methods for tracking objects, segmenting, drawing, making credits) and `moviepy.audio.tools` (currently empty, will contain denoisers and utilities for synchronization).

Tips
~~~~~

MoviePy works fine on my 1.5 petaflops supercomputer but when a clip gets very complex the rendering is slow and there is not much we can do.

- Use an interactive shell, like IPython or, better, the IPython notebook. If you don't know these, you don't know what you are missing !
- If a part of your video takes a lot of time to render, save it once and for all as a video, then use this video. Choose codec 'rawvideo' or 'png' for lossless saving.
- Prefer the ``clip.show()`` option, and use it a lot. Only use ``clip.preview()`` when really necessary.
- If the previewing is shaky, it means that your computer is not good enough to render the clip in real time. Don't hesitate to play with the options of ``preview``: for instance, lower the fps of the sound (11000 Hz is still fine) and the video.
- Prototype: design your clips separately. If your composition involves a clip that is not finished yet, replace it temporarily with a basic color clip.
- There are often several ways to produce a same effect with MoviePy, but some ways are faster. For instance don't apply effects to a whole screen video if you are only using one region of the screen afterwards: first crop the selected region, then apply your effects.
- [wishful thinking] Check on the internet or in the examples of this documentation that what you do hasn't been done before. Code shared on the internet has more chances to be optimized.


To go further and learn about all the available options and functionalities of MoviePy, see the :ref:`examples` and the reference manual. You can also browse the code of different fx


    


