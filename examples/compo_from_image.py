from moviepy import *
from moviepy.video.tools.segmenting import find_objects


# Load the image specifying the regions.
im = ImageClip("../../ultracompositing/motif.png")

# Loacate the regions, return a list of ImageClips
regions = find_objects(im)


# Load 7 clips from the US National Parks. Public Domain :D
clips = [
    VideoFileClip(n, audio=False).subclip(18, 22)
    for n in [
        "../../videos/romo_0004.mov",
        "../../videos/apis-0001.mov",
        "../../videos/romo_0001.mov",
        "../../videos/elma_s0003.mov",
        "../../videos/elma_s0002.mov",
        "../../videos/calo-0007.mov",
        "../../videos/grsm_0005.mov",
    ]
]

# fit each clip into its region
comp_clips = [
    clip.resize(r.size).with_mask(r.mask).set_pos(r.screenpos)
    for clip, r in zip(clips, regions)
]

cc = CompositeVideoClip(comp_clips, im.size)
cc.resize(0.6).write_videofile("../../composition.mp4")

# Note that this particular composition takes quite a long time of
# rendering (about 20s on my computer for just 4s of video).
