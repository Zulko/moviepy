# -*- coding: utf-8 -*-
"""Video tests meant to be run with pytest."""
import os
import sys

import pytest
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.fx.mask_color import mask_color
from moviepy.video.VideoClip import ColorClip, ImageClip

import download_media

sys.path.append("tests")
from test_helper import TMP_DIR

def test_download_media(capsys):
    with capsys.disabled():
       download_media.download()

def test_afterimage():
    with ImageClip("media/afterimage.png") as ai:
        masked_clip = mask_color(ai, color=[0,255,1]) # for green

        with ColorClip((800,600), color=(255,255,255)) as some_background_clip:

            with CompositeVideoClip([some_background_clip, masked_clip],
                                            use_bgclip=True) as final_clip:
                final_clip.duration = 5
                final_clip.write_videofile(os.path.join(TMP_DIR, "afterimage.mp4"), fps=30)

if __name__ == '__main__':
   pytest.main()
