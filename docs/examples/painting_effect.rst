=============================================
Freezing a movie frame with a painting effect
=============================================

That's an effect that we have seen a lot in westerns and such.

.. raw:: html

        <div style="position: relative; padding-bottom: 56.25%; padding-top: 30px; margin-bottom:30px; height: 0; overflow: hidden; margin-left: 5%;"><iframe type="text/html" src="https://www.youtube.com/embed/aC5CifkacSI" frameborder="0" style="position: absolute; top: 0; bottom: 10; width: 90%; height: 100%;" allowfullscreen></iframe></div>

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
