.. _efficient:

How to be efficient with MoviePy
================================

This section gathers tips and tricks to make the most of what is already known worldwide as *the MoviePy experience*. 

Let us first say that the best way to start with MoviePy is to use it with the IPython Notebook: it makes it easier to preview clips (as we will see in this section), has autocompletion, and can display the documentation for the different methods of the library.


Should I use ``moviepy.editor`` ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Most examples in this documentation use the submodule ``moviepy.editor``, but this submodule is not adapted to all needs so should *you* use it ? Short answer: if you use MoviePy to edit videos *by hand*, use it, but if you use MoviePy inside a larger library or program or webserver, it is better to avoid it and just load the functions that you need.

The module ``moviepy.editor`` can be loaded using one of the three following methods: ::


    from moviepy.editor import * # imports everything, quick and dirty
    import moviepy.editor as mpy # Clean. Then use mpy.VideoClip, etc.
    from moviepy.editor import VideoFileClip # just import what you need

With any of these lines, the ``moviepy.editor`` module will actually do a lot of work behind the curtain: It will fetch all the most common classes, functions and subpackages of MoviePy, initialize a PyGame session (if PyGame is installed) to be able to preview video clips, and implement some shortcuts, like adding the ``resize`` transformation to the clips. This way you can use ``clip.resize(width=240)`` instead of the longer ``clip.fx( resize, width=240)``. In short, ``moviepy.editor`` 
provides all you need to play around and edit your videos but it will  take time to load (circa one second). So if all you need is one or two features inside another library, it is better to import directly what you need, as follows: ::
    
    from moviepy.video.io.VideoFileClip import VideoFileClip
    from moviepy.video.fx.resize import resize


The many ways of previewing a clip
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


When you are editing a video or trying to achieve an effect with MoviePy through a trial and error process, generating the video at each trial can be very long. This section presents a few tricks to go faster.

clip.save_frame
"""""""""""""""""

Most of the time, just having one frame of the video can tell you if you are doing the right thing. You can save just one frame of the clip to a file as follows: ::
    
    my_clip.save_frame("frame.jpeg") # saves the first frame
    my_clip.save_frame("frame.png", t=2) # saves the frame a t=2s

clip.show
""""""""""

The methods ``clip.show`` and ``clip.preview`` require to have PyGame installed. PyGame must also be initialized (it will always be the case if you use the ``moviepy.editor`` module)

The method ``clip.show`` enables preview one frame of a clip without having to write it to a file: the following lines display the frame in a PyGame window ::
    
    my_clip.show() # shows the first frame of the clip
    my_clip.show(10.5) # shows the frame of the clip at t=10.5s
    my_clip.show(10.5, interactive = True)

The last line above displays the frame in an interactive way: if you click somewhere in the frame, it will print the position and color of the pixel. Press Escape to exit when you are done.
    

clip.preview
"""""""""""""

A clip previewed is generated and displayed (in a PyGame window) at the same time. ::
    
    my_clip.preview() # preview with default fps=15
    my_clip.preview(fps=25)
    my_clip.preview(fps=15, audio=False) # don't play sound.

If you click somewhere in the frames when the clip is being previewed, it will print the position and color of the pixel clicked. Press Escape abort the previewing.

Note that if the clip is complex and your computer not fast enough, the preview will appear slowed down compared to the real speed of the clip. In this case you can try to lower the frame rate (for instance to 10) or reduce the size of the clip with ``clip.resize``, it helps.

ipython_display
""""""""""""""""

When using the IPython notebook

.. image:: ../demo_preview.jpeg
    :width: 500px
    :align: center

Note that ``ipython_display`` only works when it is the last command of the cell. You can provide any valid HTML5 options. For instance, when previewing a clip that you will turn into a gif, you need the preview to start automatically and to loop (i.e. replay indefinitely), so you will write ::
    
    ipython_display(my_clip, autoplay=1, loop=1)