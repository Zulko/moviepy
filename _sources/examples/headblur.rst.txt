========================================
Tracking and blurring someone's face
========================================

.. raw:: html

        <div style="position: relative; padding-bottom: 56.25%; padding-top: 30px; margin-bottom:30px; height: 0; overflow: hidden; margin-left: 5%;"><iframe type="text/html" src="https://www.youtube.com/embed/FWCKYTRCrBI" frameborder="0" style="position: absolute; top: 0; bottom: 10; width: 90%; height: 100%;" allowfullscreen></iframe></div>

First we will need to track the face, i.e. to get two functions ``fx`` and ``fy`` such that ``(fx(t),fy(t))`` gives the position of the center of the head at time ``t``. This will be easily done with
`manual_tracking`. Then we will need to blur the area of the video around the center of the head.

.. literalinclude:: ../../examples/headblur.py
