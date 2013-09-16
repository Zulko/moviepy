=============================================
Freezing a movie frame with a painting effect
=============================================

That's an effect that we have seen a lot in westerns and such.

.. raw:: html

        <center>
        <object><param name="movie"
        value="http://www.youtube.com/v/aC5CifkacSI&hl=en_US&fs=1&rel=0">
        </param><param name="allowFullScreen" value="true"></param><param
        name="allowscriptaccess" value="always"></param><embed
        src="http://www.youtube.com/v/aC5CifkacSI&hl=en_US&fs=1&rel=0"
        type="application/x-shockwave-flash" allowscriptaccess="always"
        allowfullscreen="true" width="550" height="450"></embed></object>
        </center>

The recipe used to make a photo look like a painting:

- Find the edges of the image with the Sobel algorithm. You obtain
  what looks like a black and white hand-drawing of the photo.
- Multiply the image array to make the colors flashier, and add the contours
  obtained at the previous step.

The final clip will be the concatenation of three part: the part before
the effect, the part with the effect, and the part after the effect.
The part with the effect is obtained as follows:

- Take the frame to freeze and make a "painted image" of it. Make it a clip.
- Add a text clip saying "Audrey" to the "painted image" clip.
- Overlay the painted clip over the original frame, but make it appear and
  disappear with a fading effect.

Here you are for the code:

.. literalinclude:: ../../examples/painting_effect.py

