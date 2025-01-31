from moviepy import UpdatedVideoClip
import numpy as np
import random


class CoinFlipWorld:
    """A simulation of coin flipping.

    Imagine we want to make a video that become more and more red as we repeat same face
    on coinflip in a row because coinflip are done in real time, we need to wait
    until a winning row is done to be able to make the next frame.
    This is a world simulating that. Sorry, it's hard to come up with examples..."""

    def __init__(self, fps):
        """
        FPS is usefull because we must increment clip_t by 1/FPS to have
        UpdatedVideoClip run with a certain FPS
        """
        self.clip_t = 0
        self.win_strike = 0
        self.reset = False
        self.fps = fps

    def update(self):
        if self.reset:
            self.win_strike = 0
            self.reset = False

        print("strike : {}, clip_t : {}".format(self.win_strike, self.clip_t))
        print(self.win_strike)

        # 0 tails, 1 heads, this is our simulation of coinflip
        choice = random.randint(0, 1)
        face = random.randint(0, 1)

        # We win, we increment our serie and retry
        if choice == face:
            self.win_strike += 1
            return

        # Different face, we increment clip_t and set reset so we will reset on next update.
        # We don't reset immediately because we will need current state to make frame
        self.reset = True
        self.clip_t += 1 / self.fps

    def to_frame(self):
        """Return a frame of a 200x100 image with red more or less intense based
        on number of victories in a row."""
        red_intensity = 255 * (self.win_strike / 10)
        red_intensity = min(red_intensity, 255)

        # A 200x100 image with red more or less intense based on number of victories in a row
        return np.full((100, 200, 3), (red_intensity, 0, 0), dtype=np.uint8)


world = CoinFlipWorld(fps=5)

myclip = UpdatedVideoClip(world=world, duration=10)
# We will set FPS to same as world, if we was to use a different FPS,
# the lowest from world.fps and our write_videofile fps param
# will be the real visible fps
myclip.write_videofile("result.mp4", fps=5)
