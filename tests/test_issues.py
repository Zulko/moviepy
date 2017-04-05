"""
Tests meant to be run with pytest
"""

import os
import pytest

from moviepy.editor import *

import sys
sys.path.append("tests")
import download_media
from test_helper import PYTHON_VERSION, TMP_DIR, TRAVIS

def test_download_media(capsys):
    with capsys.disabled():
       download_media.download()

def test_issue_145():
    video = ColorClip((800, 600), color=(255,0,0)).set_duration(5)
    with pytest.raises(Exception, message="Expecting Exception"):
         final = concatenate_videoclips([video], method = 'composite')

def test_issue_285():
    clip_1 = ImageClip('media/python_logo.png', duration=10)
    clip_2 = ImageClip('media/python_logo.png', duration=10)
    clip_3 = ImageClip('media/python_logo.png', duration=10)

    merged_clip = concatenate_videoclips([clip_1, clip_2, clip_3])
    assert merged_clip.duration == 30

def test_issue_354():
    clip = ImageClip("media/python_logo.png")

    clip.duration = 10
    crosstime = 1

    #caption = editor.TextClip("test text", font="Liberation-Sans-Bold", color='white', stroke_color='gray', stroke_width=2, method='caption', size=(1280, 720), fontsize=60, align='South-East')
    #caption.duration = clip.duration
    fadecaption = clip.crossfadein(crosstime).crossfadeout(crosstime)
    ret = CompositeVideoClip([clip, fadecaption])

def test_issue_359():
    video = ColorClip((800, 600), color=(255,0,0)).set_duration(5)
    video.fps=30
    video.write_gif(filename=os.path.join(TMP_DIR, "issue_359.gif"),
                    tempfiles=True)

def test_issue_368():
    import sys
    if PYTHON_VERSION in ('2.7', '3.3'): #matplotlib only supported in python >= 3.4
       return

    #travis, python 3.5 matplotlib version has problems..
    if PYTHON_VERSION == '3.5' and TRAVIS:
       return

    import numpy as np
    import matplotlib.pyplot as plt
    from sklearn import svm
    from sklearn.datasets import make_moons
    from moviepy.video.io.bindings import mplfig_to_npimage
    import imageio

    X, Y = make_moons(50, noise=0.1, random_state=2) # semi-random data

    fig, ax = plt.subplots(1, figsize=(4, 4), facecolor=(1,1,1))
    fig.subplots_adjust(left=0, right=1, bottom=0)
    xx, yy = np.meshgrid(np.linspace(-2,3,500), np.linspace(-1,2,500))

    def make_frame(t):
        ax.clear()
        ax.axis('off')
        ax.set_title("SVC classification", fontsize=16)

        classifier = svm.SVC(gamma=2, C=1)
        # the varying weights make the points appear one after the other
        weights = np.minimum(1, np.maximum(0, t**2+10-np.arange(50)))
        classifier.fit(X, Y, sample_weight=weights)
        Z = classifier.decision_function(np.c_[xx.ravel(), yy.ravel()])
        Z = Z.reshape(xx.shape)
        ax.contourf(xx, yy, Z, cmap=plt.cm.bone, alpha=0.8,
                    vmin=-2.5, vmax=2.5, levels=np.linspace(-2,2,20))
        ax.scatter(X[:,0], X[:,1], c=Y, s=50*weights, cmap=plt.cm.bone)

        return mplfig_to_npimage(fig)

    animation = VideoClip(make_frame,duration=2)
    animation.write_gif(os.path.join(TMP_DIR, "svm.gif"),fps=20)

def test_issue_407():
    red = ColorClip((800, 600), color=(255,0,0)).set_duration(5)
    red.fps=30
    assert red.fps == 30
    assert red.w == 800
    assert red.h == 600
    assert red.size == (800, 600)

    #ColorClip has no fps attribute
    green=ColorClip((640, 480), color=(0,255,0)).set_duration(2)
    blue=ColorClip((640, 480), color=(0,0,255)).set_duration(2)

    assert green.w == blue.w == 640
    assert green.h == blue.h == 480
    assert green.size == blue.size == (640, 480)

    with pytest.raises(AttributeError, message="Expecting ValueError Exception"):
         green.fps

    with pytest.raises(AttributeError, message="Expecting ValueError Exception"):
         blue.fps

    video=concatenate_videoclips([red, green, blue])
    assert video.fps == red.fps

def test_issue_416():
    green=ColorClip((640, 480), color=(0,255,0)).set_duration(2)  #ColorClip has no fps attribute
    video1=concatenate_videoclips([green])
    assert video1.fps == None

def test_issue_417():
    # failed in python2

    cad = u'media/python_logo.png'
    myclip = ImageClip(cad).fx(vfx.resize, newsize=[1280, 660])
    final = CompositeVideoClip([myclip], size=(1280, 720))
    #final.set_duration(7).write_videofile("test.mp4", fps=30)

def test_issue_467():
    cad = 'media/python_logo.png'
    clip = ImageClip(cad)

    #caused an error, NameError: global name 'copy' is not defined
    clip = clip.fx(vfx.blink, d_on=1, d_off=1)

def test_issue_470():
    audio_clip = AudioFileClip('media/crunching.mp3')

    # t_end is out of bounds
    subclip = audio_clip.subclip(t_start=6, t_end=9)

    with pytest.raises(IOError, message="Expecting IOError"):
         subclip.write_audiofile('/tmp/issue_470.wav', write_logfile=True)

    #but this one should work..
    subclip = audio_clip.subclip(t_start=6, t_end=8)
    subclip.write_audiofile(os.path.join(TMP_DIR, 'issue_470.wav'), write_logfile=True)

def test_issue_246():
    def test_audio_reader():
        video = VideoFileClip('media/video_with_failing_audio.mp4')
        subclip = video.subclip(270)
        subclip.write_audiofile(os.path.join(TMP_DIR, 'issue_246.wav'),
                                write_logfile=True)

if __name__ == '__main__':
   pytest.main()
