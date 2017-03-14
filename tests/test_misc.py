import pytest
from moviepy.editor import *
import moviepy.video.tools.cuts as cuts

import os
import sys
sys.path.append("tests")
import download_media

def test_download_media(capsys):
    with capsys.disabled():
       download_media.download()

def test_cuts1():
    clip = VideoFileClip("media/big_buck_bunny_432_433.webm").resize(0.2)
    cuts.find_video_period(clip) == pytest.approx(0.966666666667, 0.0001)

def test_subtitles():
    from moviepy.video.tools.subtitles import SubtitlesClip

    red = ColorClip((800, 600), color=(255,0,0)).set_duration(10)
    green = ColorClip((800, 600), color=(0,255,0)).set_duration(10)
    blue = ColorClip((800, 600), color=(0,0,255)).set_duration(10)
    myvideo = concatenate_videoclips([red,green,blue])
    assert myvideo.duration == 30

    #if os.getenv("TRAVIS_PYTHON_VERSION") is None:
    if False:
       generator = lambda txt: TextClip(txt, font='Georgia-Regular',
                                     size=(800,600), fontsize=24,
                                     method='caption', align='South',
                                     color='white')
       subtitles = SubtitlesClip("media/subtitles1.srt", generator)
       final = CompositeVideoClip([myvideo, subtitles])
       final.to_videofile("/tmp/subtitles1.mp4", fps=30)
    else:
       #travis-ci doesn't like TextClip
       def generator(txt):
           class Temp:
             def __init__(self):
                 self.mask=None

           _t=Temp()
           return _t

       subtitles = SubtitlesClip("media/subtitles1.srt", generator)

    data = [([0.0, 4.0], 'Red!'), ([5.0, 9.0], 'More Red!'),
            ([10.0, 14.0], 'Green!'), ([15.0, 19.0], 'More Green!'),
            ([20.0, 24.0], 'Blue'), ([25.0, 29.0], 'More Blue!')]

    assert subtitles.subtitles == data

    subtitles = SubtitlesClip(data)
    assert subtitles.subtitles == data


if __name__ == '__main__':
   test_subtitles()
   #pytest.main()
