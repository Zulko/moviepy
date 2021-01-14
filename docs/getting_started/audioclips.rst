.. _audioclips:

Audio clips
-----------

This section shows how to use MoviePy to create and edit audio clips.

Note that when you cut, mix, or concatenate video clips in MoviePy the audio is automatically handled and you need to worry about it. This section is of interest if you just want to edit audiofiles or you want custom audio clips for your videos.

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

for more, see :class:`~moviepy.audio.io.AudioFileClip.AudioFileClip`.

Alternatively you can get the audio track of an already created video clip ::

    videoclip = VideoFileClip("some_video.avi")
    audioclip = videoclip.audio

Compositing audio clips
~~~~~~~~~~~~~~~~~~~~~~~~

:class:`~moviepy.audio.AudioClip.CompositeAudioClip` is used to combine multiple audio clips together. ::

    from moviepy import *
    first = AudioFileClip("some_audiofile.mp3")
    second = AudioFileClip("other_audiofile.mp3")
    combined = CompositeAudioClip([first, second])

The time at which clips within a ``CompositeAudioClip`` start playing is determined by their :attribute:`moviepy.Clip.start` attribute.
In the following example, ``first`` will start playing after 2 seconds and ``second`` will start 3 seconds after that. ::

    combined = CompositeAudioClip([first.with_start(2), second.with_start(5)])

If you want to play your audio clips sequentially, use :func:`moviepy.audio.AudioClip.concatenate_audioclips`.
Here, `second` only starts playing when `first` finishes. ::

    combined = concatenate_audioclips([first, second])


Exporting and previewing audio clips
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:method:`moviepy.audio.AudioClip.AudioClip.write_audiofile`

You can also assign an audio clip as the soundtrack of a video clip with ::

    videoclip2 = videoclip.with_audio(my_audioclip)
