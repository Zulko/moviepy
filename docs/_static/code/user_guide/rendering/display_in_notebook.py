from moviepy import *

# ...
# ... some jupyter specifics stuff
# ...

my_video_clip = VideoFileClip("./example.mp4")
my_image_clip = ImageClip("./example.png")
my_audio_clip = AudioFileClip("./example.wav")

# We can show any type of clip
my_video_clip.display_in_notebook()  # embeds a video
my_image_clip.display_in_notebook()  # embeds an image
my_audio_clip.display_in_notebook()  # embeds a sound

# We can display only a snaphot of a video
my_video_clip.display_in_notebook(t=1)

# We can provide any valid HTML5 option as keyword argument
# For instance, if the clip is too big, we can set width
my_video_clip.display_in_notebook(width=400)

# We can also make it loop, for example to check if a GIF is
# looping as expected
my_video_clip.display_in_notebook(autoplay=1, loop=1)
