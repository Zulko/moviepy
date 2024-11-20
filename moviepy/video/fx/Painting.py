from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageFilter

from moviepy.Clip import Clip
from moviepy.Effect import Effect


@dataclass
class Painting(Effect):
    """Transforms any photo into some kind of painting.

    Transforms any photo into some kind of painting. Saturation
    tells at which point the colors of the result should be
    flashy. ``black`` gives the amount of black lines wanted.

    np_image : a numpy image
    """

    saturation: float = 1.4
    black: float = 0.006

    def to_painting(self, np_image, saturation=1.4, black=0.006):
        """Transforms any photo into some kind of painting.

        Transforms any photo into some kind of painting. Saturation
        tells at which point the colors of the result should be
        flashy. ``black`` gives the amount of black lines wanted.

        np_image : a numpy image
        """
        image = Image.fromarray(np_image)
        image = image.filter(ImageFilter.EDGE_ENHANCE_MORE)

        # Convert the image to grayscale
        grayscale_image = image.convert("L")

        # Find the image edges
        edges_image = grayscale_image.filter(ImageFilter.FIND_EDGES)

        # Convert the edges image to a numpy array
        edges = np.array(edges_image)

        # Create the darkening effect
        darkening = black * (255 * np.dstack(3 * [edges]))

        # Apply the painting effect
        painting = saturation * np.array(image) - darkening

        # Clip the pixel values to the valid range of 0-255
        painting = np.maximum(0, np.minimum(255, painting))

        # Convert the pixel values to unsigned 8-bit integers
        painting = painting.astype("uint8")

        return painting

    def apply(self, clip: Clip) -> Clip:
        """Apply the effect to the clip."""
        return clip.image_transform(
            lambda im: self.to_painting(im, self.saturation, self.black)
        )
