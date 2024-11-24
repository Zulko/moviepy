"""Let's first concatenate (one after the other) then composite
(on top of each other) three audio clips."""

from moviepy import AudioFileClip, CompositeAudioClip, concatenate_audioclips

# We load all the clips we want to compose
clip1 = AudioFileClip("example.wav")
clip2 = AudioFileClip("example2.wav")
clip3 = AudioFileClip("example3.wav")

# All clip will play one after the other
concat = concatenate_audioclips([clip1, clip2, clip3])

# We will play clip1, then on top of it clip2 starting at t=5s,
# and clip3 on top of both starting t=9s
compo = CompositeAudioClip(
    [
        clip1.with_volume_scaled(1.2),
        clip2.with_start(5),  # start at t=5s
        clip3.with_start(9),
    ]
)
