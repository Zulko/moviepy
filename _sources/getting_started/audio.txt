.. _audio:

Audio in MoviePy
-----------------

This section shows how to use MoviePy to create and edit audio clips.

Note that when you cut, mix or concatenate video clips in MoviePy the audio is automatically handled and you need to worry about it. This section is of interest if you just want to edit audiofiles or you want custom audio clips for your videos.

Creating a new audio clip
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Audio clips can be created from an audio file or from the soundtrack of a video file
::
    from moviepy.editor import *
    audioclip = AudioFileClip("some_audiofile.mp3")
    audioclip = AudioFileClip("some_video.avi")

Alternatively you can get the audio track of an already created video clip:

    videoclip = VideoFileClip("some_video.avi")
    audioclip = videoclip.audio

You can also