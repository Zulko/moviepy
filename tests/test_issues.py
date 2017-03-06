"""
Tests meant to be run with pytest
"""

import os
import pytest

from moviepy.editor import *

# must have to work on travis-ci
import sys
sys.path.append("tests")
import download_media

def test_download_media(capsys):
    with capsys.disabled():
       download_media.download()

def test_issue_145():
    video = ColorClip((800, 600), color=(255,0,0)).set_duration(5)
    with pytest.raises(Exception, message="Expecting Exception"):
         final = concatenate_videoclips([video], method = 'composite')

def test_issue_368():
    import sys
    if sys.version_info < (3,4):   #matplotlib only supported in python >= 3.4
       return

    # $DISPLAY not set error in (travis-ci) python 3.5, so ignore 3.5 for now
    if sys.version_info.major == 3 and sys.version_info.minor ==5:
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
    animation.write_gif("/tmp/svm.gif",fps=20)


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

if __name__ == '__main__':
   pytest.main()
