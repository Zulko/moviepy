import numpy as np

from moviepy import *
from moviepy.video.tools.segmenting import find_objects


# WE CREATE THE TEXT THAT IS GOING TO MOVE, WE CENTER IT.

screensize = (720, 460)
txtClip = TextClip(
    "Cool effect", color="white", font="Amiri-Bold", kerning=5, font_size=100
)
cvc = CompositeVideoClip([txtClip.with_position("center")], size=screensize)

# THE NEXT FOUR FUNCTIONS DEFINE FOUR WAYS OF MOVING THE LETTERS


# helper function
rotMatrix = lambda a: np.array([[np.cos(a), np.sin(a)], [-np.sin(a), np.cos(a)]])


def vortex(screenpos, i, nletters):  # noqa D103
    d = lambda t: 1.0 / (0.3 + t**8)  # damping
    a = i * np.pi / nletters  # angle of the movement
    v = rotMatrix(a).dot([-1, 0])
    if i % 2:
        v[1] = -v[1]
    return lambda t: screenpos + 400 * d(t) * rotMatrix(0.5 * d(t) * a).dot(v)


def cascade(screenpos, i, nletters):  # noqa D103
    v = np.array([0, -1])
    d = lambda t: 1 if t < 0 else abs(np.sinc(t) / (1 + t**4))
    return lambda t: screenpos + v * 400 * d(t - 0.15 * i)


def arrive(screenpos, i, nletters):  # noqa D103
    v = np.array([-1, 0])
    d = lambda t: max(0, 3 - 3 * t)
    return lambda t: screenpos - 400 * v * d(t - 0.2 * i)


def vortexout(screenpos, i, nletters):  # noqa D103
    d = lambda t: max(0, t)  # damping
    a = i * np.pi / nletters  # angle of the movement
    v = rotMatrix(a).dot([-1, 0])
    if i % 2:
        v[1] = -v[1]
    return lambda t: screenpos + 400 * d(t - 0.1 * i) * rotMatrix(-0.2 * d(t) * a).dot(
        v
    )


# WE USE THE PLUGIN find_objects TO LOCATE AND SEPARATE EACH LETTER

letters = find_objects(cvc)  # a list of ImageClips


# WE ANIMATE THE LETTERS


def moveLetters(letters, funcpos):  # noqa D103
    return [
        letter.with_position(funcpos(letter.screenpos, i, len(letters)))
        for i, letter in enumerate(letters)
    ]


clips = [
    CompositeVideoClip(moveLetters(letters, funcpos), size=screensize).subclip(0, 5)
    for funcpos in [vortex, cascade, arrive, vortexout]
]

# WE CONCATENATE EVERYTHING AND WRITE TO A FILE

final_clip = concatenate_videoclips(clips)
final_clip.write_videofile("../../coolTextEffects.avi", fps=25, codec="mpeg4")
