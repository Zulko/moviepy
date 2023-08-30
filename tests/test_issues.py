"""Issue tests meant to be run with pytest."""

import os

import pytest

from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.compositing.transitions import crossfadein, crossfadeout
from moviepy.video.fx.resize import resize
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import ColorClip, ImageClip, VideoClip


try:
    import matplotlib.pyplot
except ImportError:
    matplotlib = None
else:
    matplotlib = True


def test_issue_145():
    video = ColorClip((800, 600), color=(255, 0, 0)).with_duration(5)
    with pytest.raises(Exception):
        concatenate_videoclips([video], method="composite")


def test_issue_190():
    # from PIL import Image
    #
    # filename = os.path.join(util.TMP_DIR, "issue_190.png")
    # Image.new('L', (800,600), 'white').save(filename)
    #
    # from imageio import imread
    # image = imread(filename)
    #
    # clip = ImageSequenceClip([image, image], fps=1)
    # clip.write_videofile(os.path.splitext(filename)[0] + ".mp4"))
    pass


def test_issue_285():
    clip_1, clip_2, clip_3 = (
        ImageClip("media/python_logo.png", duration=10),
        ImageClip("media/python_logo.png", duration=10),
        ImageClip("media/python_logo.png", duration=10),
    )
    merged_clip = concatenate_videoclips([clip_1, clip_2, clip_3])
    assert merged_clip.duration == 30


def test_issue_334(util):
    # NOTE: this is horrible. Any simpler version ?
    last_move = None
    last_move1 = None

    lis = [
        (0.0, 113, 167, 47),
        (0.32, 138, 159, 47),
        (0.44, 152, 144, 47),
        (0.48, 193, 148, 47),
        (0.6, 193, 148, 47),
        (0.76, 205, 138, 55),
        (0.88, 204, 121, 63),
        (0.92, 190, 31, 127),
        (1.2, 183, 59, 127),
        (1.4, 137, 22, 127),
        (1.52, 137, 22, 127),
        (1.72, 129, 67, 127),
        (1.88, 123, 69, 127),
        (2.04, 131, 123, 63),
        (2.24, 130, 148, 63),
        (2.48, 130, 148, 63),
        (2.8, 138, 180, 63),
        (3.0, 138, 180, 63),
        (3.2, 146, 192, 63),
        (3.28, 105, 91, 151),
        (3.44, 105, 91, 151),
        (3.72, 11, 48, 151),
        (3.96, 5, 78, 151),
        (4.32, 4, 134, 1),
        (4.6, 149, 184, 48),
        (4.8, 145, 188, 48),
        (5.0, 154, 217, 48),
        (5.08, 163, 199, 48),
        (5.2, 163, 199, 48),
        (5.32, 164, 187, 48),
        (5.48, 163, 200, 48),
        (5.76, 163, 200, 48),
        (5.96, 173, 199, 48),
        (6.0, 133, 172, 48),
        (6.04, 128, 165, 48),
        (6.28, 128, 165, 48),
        (6.4, 129, 180, 48),
        (6.52, 133, 166, 48),
        (6.64, 133, 166, 48),
        (6.88, 144, 183, 48),
        (7.0, 153, 174, 48),
        (7.16, 153, 174, 48),
        (7.24, 153, 174, 48),
        (7.28, 253, 65, 104),
        (7.64, 253, 65, 104),
        (7.8, 279, 116, 80),
        (8.0, 290, 105, 80),
        (8.24, 288, 124, 80),
        (8.44, 243, 102, 80),
        (8.56, 243, 102, 80),
        (8.8, 202, 107, 80),
        (8.84, 164, 27, 104),
        (9.0, 164, 27, 104),
        (9.12, 121, 9, 104),
        (9.28, 77, 33, 104),
        (9.32, 52, 23, 104),
        (9.48, 52, 23, 104),
        (9.64, 33, 46, 104),
        (9.8, 93, 49, 104),
        (9.92, 93, 49, 104),
        (10.16, 173, 19, 104),
        (10.2, 226, 173, 48),
        (10.36, 226, 173, 48),
        (10.48, 211, 172, 48),
        (10.64, 208, 162, 48),
        (10.92, 220, 171, 48),
    ]

    lis1 = [
        (0.0, 113, 167, 47),
        (0.32, 138, 159, 47),
        (0.44, 152, 144, 47),
        (0.48, 193, 148, 47),
        (0.6, 193, 148, 47),
        (0.76, 205, 138, 55),
        (0.88, 204, 121, 63),
        (0.92, 190, 31, 127),
        (1.2, 183, 59, 127),
        (1.4, 137, 22, 127),
        (1.52, 137, 22, 127),
        (1.72, 129, 67, 127),
        (1.88, 123, 69, 127),
        (2.04, 131, 123, 63),
        (2.24, 130, 148, 63),
        (2.48, 130, 148, 63),
        (2.8, 138, 180, 63),
        (3.0, 138, 180, 63),
        (3.2, 146, 192, 63),
        (3.28, 105, 91, 151),
        (3.44, 105, 91, 151),
        (3.72, 11, 48, 151),
        (3.96, 5, 78, 151),
        (4.32, 4, 134, 1),
        (4.6, 149, 184, 48),
        (4.8, 145, 188, 48),
        (5.0, 154, 217, 48),
        (5.08, 163, 199, 48),
        (5.2, 163, 199, 48),
        (5.32, 164, 187, 48),
        (5.48, 163, 200, 48),
        (5.76, 163, 200, 48),
        (5.96, 173, 199, 48),
        (6.0, 133, 172, 48),
        (6.04, 128, 165, 48),
        (6.28, 128, 165, 48),
        (6.4, 129, 180, 48),
        (6.52, 133, 166, 48),
        (6.64, 133, 166, 48),
        (6.88, 144, 183, 48),
        (7.0, 153, 174, 48),
        (7.16, 153, 174, 48),
        (7.24, 153, 174, 48),
        (7.28, 253, 65, 104),
        (7.64, 253, 65, 104),
        (7.8, 279, 116, 80),
        (8.0, 290, 105, 80),
        (8.24, 288, 124, 80),
        (8.44, 243, 102, 80),
        (8.56, 243, 102, 80),
        (8.8, 202, 107, 80),
        (8.84, 164, 27, 104),
        (9.0, 164, 27, 104),
        (9.12, 121, 9, 104),
        (9.28, 77, 33, 104),
        (9.32, 52, 23, 104),
        (9.48, 52, 23, 104),
        (9.64, 33, 46, 104),
        (9.8, 93, 49, 104),
        (9.92, 93, 49, 104),
        (10.16, 173, 19, 104),
        (10.2, 226, 173, 48),
        (10.36, 226, 173, 48),
        (10.48, 211, 172, 48),
        (10.64, 208, 162, 48),
        (10.92, 220, 171, 48),
    ]

    def posi(t):
        global last_move
        if len(lis) == 0:
            return (last_move[1], last_move[2])
        if t >= lis[0][0]:
            last_move = item = lis.pop(0)
            return (item[1], item[2])
        else:
            if len(lis) > 0:
                dura = lis[0][0] - last_move[0]
                now = t - last_move[0]
                w = (lis[0][1] - last_move[1]) * (now / dura)
                h = (lis[0][2] - last_move[2]) * (now / dura)
                # print t, last_move[1] + w, last_move[2] + h
                return (last_move[1] + w, last_move[2] + h)
            return (last_move[1], last_move[2])

    def size(t):
        global last_move1
        if len(lis1) == 0:
            return (last_move1[3], last_move1[3] * 1.33)
        if t >= lis1[0][0]:
            last_move1 = item = lis1.pop(0)
            return (item[3], item[3] * 1.33)
        else:
            if len(lis) > 0:
                dura = lis1[0][0] - last_move1[0]
                now = t - last_move1[0]
                s = (lis1[0][3] - last_move1[3]) * (now / dura)
                nsw = last_move1[3] + s
                nsh = nsw * 1.33
                # print t, nsw, nsh
                return (nsw, nsh)
            return (last_move1[3], last_move1[3] * 1.33)

    avatar = VideoFileClip("media/big_buck_bunny_432_433.webm", has_mask=True)
    avatar.audio = None
    maskclip = ImageClip("media/afterimage.png", is_mask=True, transparent=True)
    avatar.with_mask(maskclip)  # must set maskclip here..
    concatenated = avatar * 3

    tt = VideoFileClip("media/big_buck_bunny_0_30.webm").subclip(0, 3)
    # TODO: Setting mask here does not work:
    # .with_mask(maskclip).resize(size)])
    final = CompositeVideoClip([tt, concatenated.with_position(posi).fx(resize, size)])
    final.duration = tt.duration
    final.write_videofile(os.path.join(util.TMP_DIR, "issue_334.mp4"), fps=10)


def test_issue_354():
    with ImageClip("media/python_logo.png") as clip:
        clip.duration = 10
        crosstime = 1

        # TODO: Should this be removed?
        # caption = editor.TextClip("test text", font="Liberation-Sans-Bold",
        #                           color='white', stroke_color='gray',
        #                           stroke_width=2, method='caption',
        #                           size=(1280, 720), font_size=60,
        #                           align='South-East')
        # caption.duration = clip.duration

        fadecaption = clip.fx(crossfadein, crosstime).fx(crossfadeout, crosstime)
        CompositeVideoClip([clip, fadecaption]).close()


def test_issue_359(util):
    with ColorClip((800, 600), color=(255, 0, 0)).with_duration(0.2) as video:
        video.fps = 30
        video.write_gif(
            filename=os.path.join(util.TMP_DIR, "issue_359.gif"), tempfiles=True
        )


@pytest.mark.skipif(not matplotlib, reason="no matplotlib")
def test_issue_368(util):
    import matplotlib.pyplot as plt
    import numpy as np
    from sklearn import svm
    from sklearn.datasets import make_moons

    from moviepy.video.io.bindings import mplfig_to_npimage

    plt.switch_backend("Agg")

    X, Y = make_moons(50, noise=0.1, random_state=2)  # semi-random data

    fig, ax = plt.subplots(1, figsize=(4, 4), facecolor=(1, 1, 1))
    fig.subplots_adjust(left=0, right=1, bottom=0)
    xx, yy = np.meshgrid(np.linspace(-2, 3, 500), np.linspace(-1, 2, 500))

    def make_frame(t):
        ax.clear()
        ax.axis("off")
        ax.set_title("SVC classification", fontsize=16)

        classifier = svm.SVC(gamma=2, C=1)
        # the varying weights make the points appear one after the other
        weights = np.minimum(1, np.maximum(0, t**2 + 10 - np.arange(50)))
        classifier.fit(X, Y, sample_weight=weights)
        Z = classifier.decision_function(np.c_[xx.ravel(), yy.ravel()])
        Z = Z.reshape(xx.shape)
        ax.contourf(
            xx,
            yy,
            Z,
            cmap=plt.cm.bone,
            alpha=0.8,
            vmin=-2.5,
            vmax=2.5,
            levels=np.linspace(-2, 2, 20),
        )
        ax.scatter(X[:, 0], X[:, 1], c=Y, s=50 * weights, cmap=plt.cm.bone)

        return mplfig_to_npimage(fig)

    animation = VideoClip(make_frame, duration=0.2)
    animation.write_gif(os.path.join(util.TMP_DIR, "svm.gif"), fps=20)


def test_issue_407():
    red = ColorClip((800, 600), color=(255, 0, 0)).with_duration(5)
    red.fps = 30

    assert red.fps == 30
    assert red.w == 800
    assert red.h == 600
    assert red.size == (800, 600)

    # ColorClip has no fps attribute.
    green = ColorClip((640, 480), color=(0, 255, 0)).with_duration(2)
    blue = ColorClip((640, 480), color=(0, 0, 255)).with_duration(2)

    assert green.w == blue.w == 640
    assert green.h == blue.h == 480
    assert green.size == blue.size == (640, 480)

    with pytest.raises(AttributeError):
        green.fps

    with pytest.raises(AttributeError):
        blue.fps

    video = concatenate_videoclips([red, green, blue])
    assert video.fps == red.fps


def test_issue_416():
    # ColorClip has no fps attribute.
    green = ColorClip((640, 480), color=(0, 255, 0)).with_duration(2)
    video1 = concatenate_videoclips([green])
    assert video1.fps is None


def test_issue_417():
    # failed in python2
    cad = "media/python_logo.png"
    myclip = ImageClip(cad).fx(resize, new_size=[1280, 660])
    CompositeVideoClip([myclip], size=(1280, 720))
    # final.with_duration(7).write_videofile("test.mp4", fps=30)


def test_issue_470(util):
    wav_filename = os.path.join(util.TMP_DIR, "moviepy_issue_470.wav")

    audio_clip = AudioFileClip("media/crunching.mp3")

    # end_time is out of bounds
    subclip = audio_clip.subclip(start_time=6, end_time=9)

    with pytest.raises(IOError):
        subclip.write_audiofile(wav_filename, write_logfile=True)

    # but this one should work..
    subclip = audio_clip.subclip(start_time=6, end_time=8)
    subclip.write_audiofile(wav_filename, write_logfile=True)


def test_issue_547():
    red = ColorClip((640, 480), color=(255, 0, 0)).with_duration(1)
    green = ColorClip((640, 480), color=(0, 255, 0)).with_duration(2)
    blue = ColorClip((640, 480), color=(0, 0, 255)).with_duration(3)

    video = concatenate_videoclips([red, green, blue], method="compose")
    assert video.duration == 6
    assert video.mask.duration == 6

    video = concatenate_videoclips([red, green, blue])
    assert video.duration == 6


def test_issue_636():
    with VideoFileClip("media/big_buck_bunny_0_30.webm").subclip(0, 11) as video:
        with video.subclip(0, 1) as _:
            pass


def test_issue_655():
    video_file = "media/fire2.mp4"
    for subclip in [(0, 2), (1, 2), (2, 3)]:
        with VideoFileClip(video_file) as v:
            with v.subclip(1, 2) as _:
                pass
            next(v.subclip(*subclip).iter_frames())
    assert True


if __name__ == "__main__":
    pytest.main()
