import pytest
from moviepy.editor import *
import moviepy.video.tools.cuts as cuts

import os
import sys
sys.path.append("tests")
import download_media
from test_helper import TRAVIS, TMP_DIR


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

    #travis does not like TextClip.. so return for now..
    #but allow regular users to still run the test below
    if TRAVIS:
       return

    generator = lambda txt: TextClip(txt, font='Liberation-Mono',
                                     size=(800,600), fontsize=24,
                                     method='caption', align='South',
                                     color='white')

    subtitles = SubtitlesClip("media/subtitles1.srt", generator)
    final = CompositeVideoClip([myvideo, subtitles])
    final.to_videofile(os.path.join(TMP_DIR, "subtitles1.mp4"), fps=30)

    data = [([0.0, 4.0], 'Red!'), ([5.0, 9.0], 'More Red!'),
            ([10.0, 14.0], 'Green!'), ([15.0, 19.0], 'More Green!'),
            ([20.0, 24.0], 'Blue'), ([25.0, 29.0], 'More Blue!')]

    assert subtitles.subtitles == data

    subtitles = SubtitlesClip(data, generator)
    assert subtitles.subtitles == data

def test_file_to_subtitles():
    from moviepy.video.tools.subtitles import file_to_subtitles

    data = [([0.0, 4.0], 'Red!'), ([5.0, 9.0], 'More Red!'),
            ([10.0, 14.0], 'Green!'), ([15.0, 19.0], 'More Green!'),
            ([20.0, 24.0], 'Blue'), ([25.0, 29.0], 'More Blue!')]

    assert data == file_to_subtitles("media/subtitles1.srt")

if __name__ == '__main__':
   pytest.main()
