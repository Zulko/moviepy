# Import everything needed to edit video clips
from moviepy import VideoFileClip

# Load example.mp4
clip = VideoFileClip("example.mp4")

# This does nothing, as multiply_volume will return a copy of clip
# which you will loose immediatly as you don't store it
# If you was to render clip now, the audio would still be at full volume
clip.with_volume_scaled(0.1)

# This create a copy of clip in clip_whisper with a volume of only 10% the original,
# but does not modify the original clip
# If you was to render clip right now, the audio would still be at full volume
# If you was to render clip_whisper, the audio would be a 10% of the original volume
clip_whisper = clip.with_volume_scaled(0.1)

# This replace the original clip with a copy of it where volume is only 10% of
# the original. If you was to render clip now, the audio would be at 10%
# The original clip is now lost
clip = clip.with_volume_scaled(0.1)
