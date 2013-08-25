A MoviePy crash-course
-----------------------

In this section we will give you the basics to start editing your videos.

The central objects of MoviePy are video clips. To compose movies, you start by loading video clips, you modify some of them, put them all together, and write the result to a file.

What is a video clip ?
~~~~~~~~~~~~~~~~~~~~~~~~~~

A video clip is basically an object with a ``get_frame`` attribute. ``get_frame`` is a function which for a given time ``t`` returns a picture of the clip at time ``t`` (more precisely, an array of numbers representing a picture). As an example, to play a clip frame by frame, you can (but you won't have to) write something like that: ::
    
    while t < clip.duration:
        display( clip.get_frame(t) )
        t = t + 1.0/24   # for 24 frames/second

A video clip has some fundamental attributes:

- **The size** (width,height), ``clip.size``, indicates the dimensions in pixels of the clip. You can also access the clips's width and height with ``clip.w`` and ``clip.h`` respectively.
- **The duration**, ``clip.duration``, is the time after which the clip   stops playing 
- **The soundtrack**,  ``clip.sound``, which contains the sound data (an array actually) of the clip. See :ref:`CCaudioClips`

When you put several clips together (see :ref:`CompositeVideoClips`), you may have to worry about some other attributes:

- **The position** indicates where the clip will appear if you display it as part of a bigger screen. It is actually a function which for each time ``t`` returns the position ``(x(t),y(t))`` at which the clip must appear.
- **The mask**, ``clip.mask``, is an array of numbers  between 0 and 1, a 0 at some position meaning that the pixel at the same position in the picture should not be displayed. If you are not going to do anything complicated, you shouldn't worry about the mask (by default, all video clips have a mask with only ones, meaning that the picture should be completely visible). Just know that  ``clip.mask`` is actually... a clip ! More precisely, its method ``clip.mask.get_frame`` returns, for a given time, the mask that should be used when blitting the clip's frame over another picture.


Classes of video clips
~~~~~~~~~~~~~~~~~~~~~~

Video clips can be of one of these sorts:

- ``MovieClip('myHolidays.mp4')`` for clips read from a movie file. See :class:`~VideoClip.MovieClip`.
- ``ImageClip('myPic.png')`` for clips displaying a picture, for an *a priori* infinite duration. See :class:`~VideoClip.ImageClip`.
- ``ColorClip((height,width),color=(R,G,B))`` for special ImageClips of a single color. See :class:`~VideoClip.ColorClip`.
- ``TextClip('Hello public',font='Impact-Regular')`` for special ImageClips representing a text. They are automatically generated using ImageMagick. See :class:`~VideoClip.TextClip`.

To that list we should add the ``CompositeVideoClips`` that are obtained by mixing several clips together (see :ref:`CompositeVideoClips`).

Finally, a clip can be of the base class :class:`~VideoClip.VideoClip`, and have any arbitrary ``get_frame`` method. For instance the following clip represents a 460x320
screen, that will go from black (color ``[1,1,1]``) to white (color ``[255,255,255]``) in 255 seconds. ::
    
    import numpy
    from moviepy import *
    dark_picture = np.ones((320,460,3))
    def custom_get_frame(t):
        return min( int(t) , 255 ) * dark_picture
    clip = VideoClip().set_get_frame(custom_get_frame)


Modifying a clip
~~~~~~~~~~~~~~~~

You will find many pre-implemented methods to modify a clip  in the reference manual. For instance ``clip.subclip(15,20)`` returns the part of ``clip`` that is playing between 15 seconds and 20 seconds, ``clip.resize((width, height))`` will change the resolution of the clip, while ``clip.crop`` will enable you to keep only a region of the clip and ``clip.speedx(0.5)`` will make your clip play two times slower. When it is relevant, these methods are also applied to the sound and the mask of the clip, so that you don't have to worry about modifying these.


In MoviePy **no modification of a clip occurs inplace**, which means that the result of ``clip.resize``, ``clip.speedx``, etc., will be a new clip and the original clip will be untouched. ::
    
    clip = MovieClip('myHolidays.mp4')
    clip.resize((460,320)) # ``clip`` is NOT modified
    clip = clip.resize((460,320)) # ``clip`` is modified

Another important aspect is that modified clips are just *special views* of the original clip, they do not carry all the video data with them. Actually, the *real* modifications are only performed when you are rendering the clip (see :ref:`renderingAClip`). This means that all the clip objects that you will create through modifications of other clips take virtually no place in the memory and are created instantly.

Apart from the pre-implemented modifications, you can modify a clip as you want using custom filters. You can change the timeline of the clip like this: ::
    
    modifiedClip1 = myClip.fl_time(lambda t: 3*t)
    modifiedClip2 = myClip.fl_time(lambda t: 1+sin(t))
     
Now the clip ``modifiedClip1`` plays the same as ``myClip``, only three times faster, while ``modifiedClip2`` will play ``myClip`` by oscillating between the times t=0s and t=2s. Note that in the last case you have created a clip of infinite duration (which is not a problem for the moment).

You can also modify the display of a clip. The following takes a clip and inverts the green and blue channels: ::
    
    modifiedClip = myClip.fl_image(lambda im: im[:,:,[0,2,1]])

Finally, you may want to process the clip by taking into account the time and the picture at the same time. This is possible with ``clip.fl``. The filter must be a function which takes two arguments and returns a picture. the fist argument is a ``get_frame`` method (i.e. a function which given a time returns a picture), and the second argument is the time.  ::
    
    modifiedClip = myClip.fl(lambda gf,t: np.minimum(int(t),gf(2*t))

This last one is a little complicated to grasp. ``modifiedClip`` is now a version of ``myClip``, only two times faster, and with some sort of a fade-in effect.




.. _CompositeVideoClips:

Composite video clips
~~~~~~~~~~~~~~~~~~~~~

Composite video clips are video clips which will display the contents of several other video clips. The simplest compositing is concatenation with :meth:`~VideoClip.concat`: ::
    
    video = concat([clip1,clip2,clip3])

Now ``myVideo`` is a clip that plays the clips 1, 2, and 3 one after the other. You can also play a transition clip between the clips with the option ``transition=myClip``.

Next, you have the composite videoclip: ::
    
    video = CompositeVideoClip(clip1.size, [clip1,clip2,clip3])
 
Now ``myVideo`` is a clip that has the size of ``clip1``, and plays ``clip1``, and ``clip2`` *on top of* ``clip1``, and ``clip3`` on top of
``clip1``, and ``clip2``. Of course, if ``clip2`` and ``clip3`` have the same size as ``clip1``, then only ``clip3``, which is on top, will be
visible in the video... unless  ``clip3`` and ``clip2`` have masks which hide parts of them.

You can set the starting time of each clip as follows: ::
    
    video = CompositeVideoClip(clip.size, [clip1,clip2,clip3])

Because the three clips overlap, we can make them appear with a fading-in effect. Here we go for fadein effects that last 1.5 seconds: ::
    
    video = CompositeVideoClip(clip1.size, [clip1, # starts at t=0
                                          clip2.set_start(50).fadein(1.5),
                                          clip3.set_start(90).fadein(1.5)])

Finally, if ``clip2`` and ``clip3`` are smaller than ``clip1``, you can decide where they will appear: ::
    
    video = CompositeVideoClip(clip1.size,
                              [clip1,
                               clip2.set_pos((45,150)),
                               clip3.set_pos((90,100))])

Note that there are many ways to specify the position: ::
    
    clip2.set_pos((45,150)) # x=45, y=150
    
    # clip2 is horizontally centered, and at the top of the picture
    clip2.set_pos(("center","top"))
    
    # clip2 is at 40% of the width, 70% of the height:
    clip2.set_pos((0.4,0.7), relative=True)
    
    # clip2's position is horizontally centered, and moving up !
    clip2.set_pos(lambda t: ('center', 50+t) )

Be careful when indicating the position that the ``y`` position has its
zero at the top of the picture:

.. figure:: videoWH.jpeg



.. _renderingAClip:

Rendering a video clip
~~~~~~~~~~~~~~~~~~~~~~~

The ``duration`` attribute must be set (with ``clip.set_duration``) to be able to preview or write the movie to a file (some clips, like clips displaying a picture, have *a priori* an infinite duration).

To display one frame of the clip, you type one of these: ::
    
    myClip.show() # shows the first frame of the clip
    myClip.show(10.5) # shows the frame of the clip at t=10.5s
    myClip.show(10.5,frontend="matplotlib") # show in a matplotlib window

To preview the clip, you type::
    
    myClip.preview() # preview with default fps=15
    myClip.preview(fps=25)
    myClip.preview(fps=15, audio=False) # Play the clip with no sound.

It is important to note that the ``fps`` can be any number, independently of the ``fps`` of your different sources.

To write a clip as a video file, use ::
    
    myClip.to_movie("myEditedMovie.avi") # default codec: 'DIVX' fps: 24
    myClip.to_movie("myEditedMovie.avi",fps=24, codec='raw') # raw movie
    myClip.to_movie("myEditedMovie.avi",audio=False) # don't render the audio.

The codec *DIVX* will produce very light yet good quality movies, while the *raw* codec will produce very large movies with perfect quality. Many other codecs are available.


.. _CCaudioClips:

Audio clips
~~~~~~~~~~~~~

The second important objects of MoviePy are the audio clips. If ``myHolidays.mp4`` is a video with sound, then ::
    
    clip = MovieClip('myHolidays.mp4', audio=True)

will create a clip with a ``clip.sound`` attribute which is an audio clip. This is the sound that you will hear if you render the clip with ``clip.preview`` or ``clip.to_movie``. You can also create an audio clip from a sound file and then attach it to a video clip: ::
        
    audio = SoundClip('mySong.wav')
    video = MovieClip('myHolidays.mp4').set_audio(audio)

Like video clips, audio clips can be cut (with ``clip.subclip``) modified (with for instance ``clip.volumex`` which multiplies the volume) and combined (with ``CompositeAudioClip``). But most of the time, MoviePy will do that for you:

- When you cut a video clip with ``videoclip.subclip(20,25)`` then the sound will also be cut, i.e. the resulting clip will have an audio clip ``videoclip.audio.subclip(20,25)``.
- When you put several clips together in a CompositeVideoClip, then the sound of the CompositeVideoClip will be the composition of the sounds of the different video clips.

For an example, you can refer to :ref:`soundexample`. Like video clips, sound clips have a ``get_frame`` attribute, and creating new audio clips by modifying or putting together other audio clips does not take place in the memory. The actual sounds of the audio clips are only computed when we ask to play them or to write them to a file. You can do that as follows: ::
    
    audioclip.preview() # default fps: 22050
    audioclip.preview(fps=44100)
    audioclip.to_soundfile('myclip.wav',fps=44100) #default fps: 22050

Going further
~~~~~~~~~~~~~~

Now you should understand the scripts given in :ref:`examples`, and you should be able to write your own scripts. To go further and learn about all the available options and functionalities of MoviePy, see the :ref:`cookbook` and the reference manual.


    


