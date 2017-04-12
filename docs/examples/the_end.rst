======================
"The End" effect
======================

.. raw:: html

        <div style="position: relative; padding-bottom: 56.25%; padding-top: 30px; margin-bottom:30px; height: 0; overflow: hidden; margin-left: 5%;"><iframe type="text/html" src="https://www.youtube.com/embed/sZMyzzGlsc0" frameborder="0" style="position: absolute; top: 0; bottom: 10; width: 90%; height: 100%;" allowfullscreen></iframe></div>

So let's explain this one: there is a clip with "The End" written in the middle, and *above* this
clip there is the actual movie. The actual movie has a mask which represents
a white (=opaque) circle on a black (=transparent) background. At the begining,
that circle is so large that you see all the actual movie and you don't see
the "The End" clip. Then the circle becomes progressively smaller and as a
consequence you see less of the actual movie and more of the "The End" clip.

.. literalinclude:: ../../examples/the_end.py
