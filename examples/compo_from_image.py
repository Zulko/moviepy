from moviepy.all import *
from moviepy.plugins.segmenting import findObjects

# Load the image specifying the regions.
im = ImageClip("../../ultracompositing/motif.png")

# Loacate the regions, return a list of ImageClips
regions = findObjects(im)


# Load 7 clips from the US National Parks. Public Domain :D
clips = [VideoFileClip(n, audio=False).subclip(18,22) for n in
     [ "../../videos/romo_0004.mov",
      "../../videos/apis-0001.mov",
      "../../videos/romo_0001.mov",
      "../../videos/elma_s0003.mov",
      "../../videos/elma_s0002.mov",
      "../../videos/calo-0007.mov",
      "../../videos/grsm_0005.mov"]]

# fit each clip into its region
comp_clips =  [c.fx(vfx.resize, r.size).\
                 set_mask(r.mask).\
                 set_pos(r.screenpos)
               for c,r in zip(clips,regions)]

cc = CompositeVideoClip(comp_clips,im.size)
cc.fx( vfx.resize, 0.6).to_videofile("../../bigcompo.avi")

# Note that this particular composition takes quite a long time of
# rendering (about 20s on my computer for just 4s of video).
