from dataclasses import dataclass

from moviepy.Clip import Clip
from moviepy.Effect import Effect


@dataclass
class Crop(Effect):
    """Effect to crop a clip to get a new clip in which just a rectangular
    subregion of the original clip is conserved. `x1,y1` indicates the top left
    corner and `x2,y2` is the lower right corner of the cropped region. All
    coordinates are in pixels. Float numbers are accepted.

    To crop an arbitrary rectangle:

    >>> Crop(x1=50, y1=60, x2=460, y2=275)

    Only remove the part above y=30:

    >>> Crop(y1=30)

    Crop a rectangle that starts 10 pixels left and is 200px wide

    >>> Crop(x1=10, width=200)

    Crop a rectangle centered in x,y=(300,400), width=50, height=150 :

    >>> Crop(x_center=300, y_center=400, width=50, height=150)

    Any combination of the above should work, like for this rectangle
    centered in x=300, with explicit y-boundaries:

    >>> Crop(x_center=300, width=400, y1=100, y2=600)

    """

    x1: int = None
    y1: int = None
    x2: int = None
    y2: int = None
    width: int = None
    height: int = None
    x_center: int = None
    y_center: int = None

    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""
        if self.width and self.x1 is not None:
            self.x2 = self.x1 + self.width
        elif self.width and self.x2 is not None:
            self.x1 = self.x2 - self.width

        if self.height and self.y1 is not None:
            self.y2 = self.y1 + self.height
        elif self.height and self.y2 is not None:
            self.y1 = self.y2 - self.height

        if self.x_center:
            self.x1, self.x2 = (
                self.x_center - self.width / 2,
                self.x_center + self.width / 2,
            )

        if self.y_center:
            self.y1, self.y2 = (
                self.y_center - self.height / 2,
                self.y_center + self.height / 2,
            )

        self.x1 = self.x1 or 0
        self.y1 = self.y1 or 0
        self.x2 = self.x2 or clip.size[0]
        self.y2 = self.y2 or clip.size[1]

        return clip.image_transform(
            lambda frame: frame[
                int(self.y1) : int(self.y2), int(self.x1) : int(self.x2)
            ],
            apply_to=["mask"],
        )
