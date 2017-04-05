import pytest
from moviepy.editor import *

# must have to work on travis-ci
import sys
sys.path.append("tests")
import download_media

def test_download_media(capsys):
    with capsys.disabled():
       download_media.download()

def test_afterimage():
    ai=ImageClip("media/afterimage.png")
    masked_clip = vfx.mask_color(ai, color=[0,255,1]) # for green

    some_background_clip = ColorClip((800,600), color=(255,255,255))

    final_clip = CompositeVideoClip([some_background_clip, masked_clip],
                                    use_bgclip=True)
    final_clip.duration=5
    final_clip.write_videofile("/tmp/afterimage.mp4", fps=30)

if __name__ == '__main__':
   pytest.main()
