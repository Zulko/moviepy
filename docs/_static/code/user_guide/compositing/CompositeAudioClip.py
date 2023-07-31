from moviepy import *

# We load all the clips we want to compose
aclip1 = AudioFileClip("example.wav")
aclip2 = AudioFileClip("example2.wav")
aclip3 = AudioFileClip("example3.wav")

# All clip will play one after the other
concat = concatenate_audioclips([aclip1, aclip2, aclip3])

# We will play aclip1, then ontop of it aclip2 after 5s, and the aclip3 on top of both after 9s
compo = CompositeAudioClip(
    [
        aclip1.with_multiply_volume(1.2),
        aclip2.with_start(5),  # start at t=5s
        aclip3.with_start(9),
    ]
)
