.. _audioclips:

Audio in MoviePy
-----------------

This section shows how to use MoviePy to create and edit audio clips.

Note that when you cut, mix or concatenate video clips in MoviePy the audio is automatically handled and you need to worry about it. This section is of interest if you just want to edit audiofiles or you want custom audio clips for your videos.

What audioclips are made of
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

AudioClips are very similar to video clips in moviepy: they have a length, can be cut and composed the same way, etc. A notable difference  be composed
``audioclip.get_frame(t)``

Creating a new audio clip
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Audio clips can be created from an audio file or from the soundtrack of a video file ::

    from moviepy.editor import *
    audioclip = AudioFileClip("some_audiofile.mp3")
    audioclip = AudioFileClip("some_video.avi")

for more, see :py:class:`~moviepy.audio.io.AudioFileClip.AudioFileClip`.

Alternatively you can get the audio track of an already created video clip ::

    videoclip = VideoFileClip("some_video.avi")
    audioclip = videoclip.audio

Compositing audio clips
~~~~~~~~~~~~~~~~~~~~~~~~

Exporting and previewing audio clips
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can also export assign an audio clip as the soundtrack of a video clip with ::

    videoclip2 = videoclip.set_audio(my_audioclip)
